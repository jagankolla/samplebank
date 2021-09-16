from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, request
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from datetime import datetime
from django.db.models import Count
from services.models import *
from .models import Profiles
from .serializers import ProfilesSerializer, DebitcardsSerializer, CreditcardsSerializer, NetbankingSerializer, \
    NetBankingTxnSerializer, DebitcardTxnSerializer, CreditcardTxnSerializer, CreditcardTxnReasonSerializer, \
    CategoryWiseCreditcardTxnSerializer
from .utils import *


@csrf_exempt  # cross site request forgery
def login(request=None):

    if request.method == 'POST':
        data = JSONParser().parse(request)
        user_name = data.get('user_name', None)
        password = data.get('password', None)
        if user_name and password:

            user_name=user_name.strip()
            password=password.strip()
        else:
            return JsonResponse({"status_code": "422", 'message':"mandatory fields missing"}, status=200)

        customer = Netbanking.objects.filter(user_name=user_name, password=password)
        if customer:
            serializer = NetbankingSerializer(customer,many=True)
            records = serializer.data
            for record in records:
                profile_id=record["profile_id"]
                print(profile_id)
                profile=Profiles.objects.get(profile_id=profile_id)
                serializer = ProfilesSerializer(profile)

                return JsonResponse({"status_code": "200", 'record': serializer.data}, status=200)

        else:
            return JsonResponse({'status_code': "400", 'message': 'Invalid credentials.'}, status=200)


@csrf_exempt  # cross site request forgery
def account_transaction(request=None):
    if request.method == 'GET':
        account_number = request.GET.get('account_number', None)
        try:
            customer = Profiles.objects.get(account_number=account_number)
            if customer:
                debited_amount_transactions = Netbanking_transaction.objects.filter(source_account_number=account_number)
                netbanking_txn_serializer = NetBankingTxnSerializer(debited_amount_transactions, many=True)
                debited_amount_records = netbanking_txn_serializer.data

                debited_amount_transactions = Debitcard_transactions.objects.filter(source_account_number=account_number)
                debitcard_txn_serializer = DebitcardTxnSerializer(debited_amount_transactions, many=True)
                debited_amount_records += debitcard_txn_serializer.data

                credited_amount_transactions = Netbanking_transaction.objects.filter(destination_account_number=account_number)
                netbanking_txn_serializer = NetBankingTxnSerializer(credited_amount_transactions, many=True)
                credited_amount_records = netbanking_txn_serializer.data

                credited_amount_transactions = Debitcard_transactions.objects.filter(destination_account_number=account_number)
                debitcard_txn_serializer = DebitcardTxnSerializer(credited_amount_transactions,many=True)
                credited_amount_records += debitcard_txn_serializer.data

                return JsonResponse({'status_code': "200", 'debited_records': debited_amount_records, 'credited_records': credited_amount_records}, status=200)
            else:
                return JsonResponse({'status_code': "404", 'message': "You dont have any account with our bank or Invalid account number"}, status=200)
        except Exception as e:
            return JsonResponse({'status_code': "400", 'message': str(e)}, status=200)


@csrf_exempt  # cross site request forgery
def net_banking_transaction(request=None):
    if request.method == 'POST':

        data = JSONParser().parse(request)
        user_name = data.get('user_name', None)
        password = data.get('password', None)
        destination_account_number = data.get('destination_account_number', None)
        transaction_amount = data.get('transaction_amount', None)

        key_list = ["user_name", "password", "destination_account_number", "transaction_amount"]
        for key in key_list:
            if key not in data.keys():
                return JsonResponse({"status_code": '422', 'message': " Missing mandatory field '" + key + "'"},
                                    status=200)

        try:
            customer_net_banking_details = Netbanking.objects.get(user_name=user_name)
            source_account_number = customer_net_banking_details.profile_id.account_number
            customer = Profiles.objects.get(account_number=source_account_number)
        except ObjectDoesNotExist:
            return JsonResponse({'status_code': "403", 'message': 'profile does not exists with our bank'}, status=200)

        if (customer_net_banking_details.user_name == user_name) and (
                customer_net_banking_details.password == password):
            if (int(transaction_amount) > 0) and (int(transaction_amount) <= int(customer.account_balance)):
                customer.account_balance = (int(customer.account_balance) - int(transaction_amount))
                customer.save()

                try:
                    destination_customer = Profiles.objects.get(account_number=destination_account_number)
                    destination_customer.account_balance = (int(destination_customer.account_balance) + int(transaction_amount))
                    destination_customer.save()

                except ObjectDoesNotExist:
                    return JsonResponse(
                        {'status_code': "200", 'message': ' Transaction successful, but the destinationcustomer is not our bank customer', 'is_destination_found': False},
                        status=200)
            else:
                return JsonResponse({'status_code': "404", 'message': 'Insufficient funds in your account'}, status=200)

            v = Netbanking_transaction(profile_id=customer, source_account_number=source_account_number,
                                       destination_account_number=destination_account_number,
                                       transaction_amount=transaction_amount)
            v.save()

            return JsonResponse({'status_code':"200",'message': "transaction successful"}, status=200)

        else:
            return JsonResponse({'status_code':"401",'message': " Invalid net banking details"}, status=200)


@csrf_exempt  # cross site request forgery
def net_banking_crud(request=None):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        account_number = data.get('account_number', None)
        user_name = data.get('user_name', None)
        password = data.get('password', None)
        net_banking_status = data.get('net_banking_status', None)

        key_list = ["account_number", "user_name", "password", "net_banking_status"]
        for key in key_list:
            if key not in data.keys():
                return JsonResponse({"status_code":'422','message': " Missing mandatory field " + key}, status=200)

        try:
            customer = Profiles.objects.get(account_number=account_number)
            if customer.net_banking=="Issued":
                return JsonResponse({"status_code": "409", 'message': "customer already having net banking"}, status=200)

            if customer.age >= 22:
                try:
                    Netbanking.objects.get(user_name=user_name)
                    return JsonResponse({"status_code": "404", 'message': 'user name is already taken'}, status=200)
                except ObjectDoesNotExist:
                    pass
                v = Netbanking(profile_id=customer, net_banking_status=net_banking_status, user_name=user_name, password=password)
                v.save()

                customer.net_banking = "Issued"
                customer.save()

                serializer = NetbankingSerializer(v)
                record = serializer.data
                return JsonResponse({"status_code":"200",'message': record}, status=200)

            else:
                return JsonResponse({"status_code":"204",'message': 'You are not eligible to get net banking as your age is not greater than or equal to 22'},
                status=200)

        except ObjectDoesNotExist:
            return JsonResponse({"status_code":"400",'message': 'You dont have any account with our bank'}, status=200)

    if request.method == 'PUT':
        data = JSONParser().parse(request)
        profile_id = data.get('profile_id', None)
        user_name = data.get('user_name', None)
        password = data.get('password', None)
        net_banking_status = data.get('net_banking_status', None)

        key_list = ["profile_id"]
        for key in key_list:
            if key not in data.keys():
                return JsonResponse({"status_code": '422', 'message': " Missing mandatory field " + key}, status=200)
        try:
            customer = Netbanking.objects.get(profile_id=profile_id)

            if user_name:
                customer.user_name = user_name

            if password:
                customer.password = password

            if net_banking_status:
                customer.net_banking_status = net_banking_status

            customer.save()

            serializer = NetbankingSerializer(customer)
            record = serializer.data
            return JsonResponse({'status_code':'200','message': 'record updated successfully', 'record': record}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({'status_code':'400','message': 'Invalid Profile Id'}, status=400)


@csrf_exempt  # cross site request forgery
def credit_card_transaction(request=None):
    if request.method == 'POST':

        data = JSONParser().parse(request)
        credit_card_number = data.get('credit_card_number', None)
        category = data.get('transaction_category')
        credit_card_expiry_dates = data.get('credit_card_expiry_dates', None)
        credit_card_cvv = data.get('credit_card_cvv', None)
        credit_card_pin = data.get('credit_card_pin', None)
        transaction_amount = data.get('transaction_amount', None)

        try:
            customer_credit_card_details = Creditcards.objects.get(credit_card_number=credit_card_number)
        except ObjectDoesNotExist:
            return JsonResponse({'status_code': "404", 'message': 'No such credit card exist with this bank'},
                                status=200)

        if customer_credit_card_details.credit_card_status!="active":
            return JsonResponse(
                {'status_code': "201", 'message': 'Your credit card is in deactivated state or blocked. please activate to do transactions or apply new card.'},
                status=200)

        elif (customer_credit_card_details.credit_card_number == credit_card_number) and \
                (customer_credit_card_details.credit_card_status=='active') and (
                customer_credit_card_details.credit_card_expiry_dates == credit_card_expiry_dates) and (
                customer_credit_card_details.credit_card_cvv == credit_card_cvv) and (customer_credit_card_details.credit_card_pin == credit_card_pin):

            if (int(transaction_amount) > 0) and (int(transaction_amount) <= int(customer_credit_card_details.credit_card_limit)):
                customer_credit_card_details.available_credit_card_limit = int(customer_credit_card_details.available_credit_card_limit) - int(transaction_amount)
                customer_credit_card_details.current_outstanding_bill = int(customer_credit_card_details.current_outstanding_bill) + int(transaction_amount)
                customer_credit_card_details.save()

            else:
                return JsonResponse({'status_code': "404", 'message': 'Insufficient  credit card limit'}, status=200)

            v = Creditcard_transactions(profile_id=customer_credit_card_details.profile_id, transaction_category=category,
                                        credit_card_number=credit_card_number, transaction_amount=transaction_amount)
            v.save()

            return JsonResponse({'status_code': "200", 'message': "Transaction Successful"}, status=200)

        else:
            return JsonResponse({'status_code': "403", 'message': " Invalid credit card details"}, status=200)

    if request.method == 'GET':
        credit_card_number = request.GET.get('credit_card_number', None)

        try:
            customer = Creditcard_transactions.objects.filter(credit_card_number=credit_card_number)
            if customer:
                serializer = CreditcardTxnSerializer(customer, many=True)
                records = serializer.data
                return JsonResponse({"status_code": "200", 'record': records}, status=200)
            else:
                return JsonResponse({"status_code": "404", 'message': "No records found with this credit card number. or invalid credit card number."}, status=200)
        except Exception:
            return JsonResponse(
                {'status_code': "400", 'message': 'Error in your code.'},
                status=200)


@csrf_exempt  # cross site request forgery
def spend_analyzer(request=None):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        credit_card_number = data.get('credit_card_number', None)  # mandatory field
        # reason_filter, start_date and end_date are optional fields
        transaction_category = data.get('transaction_category')
        # start_date and end_date must come in combination
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        categories = {}
        category_wise_txn_amount ={}
        final_records = []
        total_no_of_txns = 0
        total_amount_spent = 0.0
        customer_reasons_for_txns_list = []
        category_wise_txn_amount_in_percentages = {}
        categories_not_present_in_final_records = []
        is_category_found = False

        # if (start_date and end_date is None) or (end_date and start_date is None):
        #     return JsonResponse({"status_code": "422", "message": "start_date and end_date must come in combination"})

        try:
            customer = Creditcard_transactions.objects.filter(credit_card_number=credit_card_number)
            customer_reasons_for_txns = Creditcard_transactions.objects.filter(credit_card_number=credit_card_number).only("transaction_category")
            if customer:
                # if reason_filter:
                #     records = customer.annotate(transaction_reason=reason_filter)
                #     # records = customer.raw("SELECT * FROM SERVICES_CREDITCARD_TRANSACTIONS GROUP BY TRANSACTION_REASON")
                # elif start_date and end_date:
                #     start_date_list = start_date.split("/")
                #     end_date_list = end_date.split("/")
                #     start_date = datetime(start_date_list[2], start_date_list[1], start_date_list[0])
                #     end_date = datetime(end_date_list[2], end_date_list[1], end_date_list[0])
                #     records = customer.filter(transaction_time__range=(start_date, end_date))
                # else:
                #     records = customer

                # serialize the credit card txn records
                serializer = CreditcardTxnSerializer(customer, many=True)
                records = serializer.data

                # serialize the transaction reasons
                customer_reasons_for_txns_serializer = CreditcardTxnReasonSerializer(customer_reasons_for_txns, many=True)
                customer_reasons_for_txns = customer_reasons_for_txns_serializer.data

                for my_dict in customer_reasons_for_txns:
                    customer_reasons_for_txns_list.append(my_dict["transaction_category"])
                customer_reasons_for_txns = list(set(customer_reasons_for_txns_list))

                # prepare categories dict -  to maintain no of txns done for each reason(category)
                for reason in customer_reasons_for_txns:
                    categories[reason] = 0

                # no of txns done in each category is achieved here
                for record in records:
                    for reason in categories:
                        if record['transaction_category'] == reason:
                            categories[reason] += 1

                # calculating total no of txns
                for no_of_txns in categories.values():
                    total_no_of_txns += no_of_txns

                # prepare categories dict -  to maintain amount spent based on each category
                for reason in customer_reasons_for_txns:
                    category_wise_txn_amount[reason] = 0

                # calculating category wise txn amount
                for record in records:
                    for reason in category_wise_txn_amount:
                        if record['transaction_category'] == reason:
                            category_wise_txn_amount[reason] += float(record['transaction_amount'])

                # calculating total amount of expenditure
                for no_of_txns in category_wise_txn_amount.values():
                    total_amount_spent += no_of_txns

                # percentage of amount spent in each category
                for reason, amount in category_wise_txn_amount.items():
                    category_wise_txn_amount_in_percentages[reason] = round((amount/total_amount_spent)*100, 2)

                # formatting the output records
                categories_list = categories.keys()
                if categories_list:
                    # for category in categories_list:
                        # # records based on category separately
                        # category_records = customer.filter(transaction_category=category)
                        # # if category not in final_records:
                        # #     final_records[category] = {}
                        # # serialize the credit card txn records
                        # category_wise_credit_card_serializer = CategoryWiseCreditcardTxnSerializer(category_records, many=True)
                        # category_wise_credit_card_records = category_wise_credit_card_serializer.data
                        # # final_records[category]['records'] = category_wise_credit_card_records
                        # #
                        # # add records here based on the no of transactions by category
                        # final_records[category]['no_of_transactions'] = categories[category]
                        #
                        # # add records here based on the txn amount in percentages based category
                        # final_records[category]['transaction_amount_in_percentage'] = str(category_wise_txn_amount_in_percentages[category])+"%"
                        #
                        # # add records here based on the txn amount in percentages based category
                        # final_records[category]['amount_spent'] = category_wise_txn_amount[category]

                    # get all the categories which are not present in final records into a list
                    for category in categories_list:
                        for category_record in final_records:
                            if category_record['category'] == category:
                                is_category_found = True
                                break
                        if is_category_found is False:
                            categories_not_present_in_final_records.append(category)

                    for category in categories_not_present_in_final_records:
                        # records based on category
                        category_records = customer.filter(transaction_category=category)
                        # serialize the credit card txn records
                        category_wise_credit_card_serializer = CategoryWiseCreditcardTxnSerializer(category_records,
                                                                                                   many=True)
                        category_wise_credit_card_records = category_wise_credit_card_serializer.data
                        category_record = {'category': category, 'records': category_wise_credit_card_records,
                                           'no_of_transactions': categories[category],
                                           'amount_spent': category_wise_txn_amount[category],
                                           'transaction_amount_in_percentage': str(
                                            category_wise_txn_amount_in_percentages[category]) + "%"
                                           }
                        final_records.append(category_record)

                    return JsonResponse({"status_code": "200",
                                         'total_no_of_transactions': total_no_of_txns,
                                         'total_amount_spent': total_amount_spent,
                                         'data': final_records}, status=200)
            else:
                return JsonResponse({"status_code": "404",
                                     'message': "No records found with this credit card number. or invalid credit card number."},
                                    status=200)
        except Exception as e:
            return JsonResponse(
                {'status_code': "400", 'message': e}, status=200)


@csrf_exempt  # cross site request forgery
def credit_card_crud(request=None):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        account_number = data.get('account_number', None)
        credit_card_limit = data.get('credit_card_limit', None)
        available_credit_card_limit = data.get('available_credit_card_limit', None)

        key_list = ["account_number", "credit_card_limit", "available_credit_card_limit"]
        for key in key_list:
            if key not in data.keys():
                return JsonResponse({'message': " Missing mandatory field " + key, "status_code": "422"}, status=200)

        customer_exists = Profiles.objects.get(account_number=account_number)
        if customer_exists.credit_card == "Issued":
            return JsonResponse({'message': "customer has already taken credit card", "status_code": "409"}, status=200)
        try:
            customer = Profiles.objects.get(account_number=account_number)
            if customer.age >= 22:
                credit_card_number = creditcard_number_creation()
                credit_card_expiry_dates = card_expiry_calculator()
                credit_card_cvv = cvv_creation(3)

                v = Creditcards(profile_id=customer, credit_card_number=credit_card_number,
                                credit_card_cvv=credit_card_cvv, available_credit_card_limit=available_credit_card_limit, credit_card_expiry_dates=credit_card_expiry_dates,
                                credit_card_limit=credit_card_limit)
                v.save()

                customer.credit_card = "Issued"
                customer.save()

                serializer = CreditcardsSerializer(v)
                record = serializer.data
                return JsonResponse({'status_code': '200', 'record': record}, status=200)

            else:
                return JsonResponse({'status_code': '204', 'message': 'You are not eligible to get credit card as your age is not greater than or equal to 22'},
                                    status=200)

        except ObjectDoesNotExist:
            return JsonResponse({'status_code':'400','message': 'You dont have any account with our bank'}, status=200)

    if request.method == 'PUT':
        data = JSONParser().parse(request)
        profile_id = data.get('profile_id', None)
        credit_card_limit = data.get('increasing_credit_card_limit', None)
        credit_card_pin = data.get('credit_card_pin', None)
        credit_card_status = data.get('credit_card_status', None)
        credit_card_bill_paying_amount = data.get('credit_card_bill_paying_amount', "0")

        try:
            key_list = ["profile_id"]
            for key in key_list:
                if key not in data.keys():
                    return JsonResponse({'message': " Missing mandatory field " + key, "status_code": "422"},status=200)

            customer = Creditcards.objects.get(profile_id=profile_id)

            if credit_card_limit:
                customer.credit_card_limit = int(customer.credit_card_limit)+int(credit_card_limit)
                customer.available_credit_card_limit = int(customer.available_credit_card_limit)+int(credit_card_limit)

            if credit_card_bill_paying_amount>"0":
                if int(customer.current_outstanding_bill)>=int(credit_card_bill_paying_amount):
                    customer.current_outstanding_bill = int(customer.current_outstanding_bill)-int(credit_card_bill_paying_amount)
                    customer.available_credit_card_limit = int(customer.available_credit_card_limit)+int(credit_card_bill_paying_amount)
                    customer.save()
                    return JsonResponse({'message': "Your credit card bill payment of rupees " + credit_card_bill_paying_amount +" is successful.", "status_code": "200"},status=200)
                else:
                    return JsonResponse({'message': "Billing amount should be greater than zero and should be less than or equal to current outstanding bill", "status_code": "202"},status=200)

            if credit_card_pin:
                customer.credit_card_pin = credit_card_pin

            if credit_card_status:
                if credit_card_status == "blocked":
                    if int(customer.current_outstanding_bill)!=0:
                        return JsonResponse({'message': "To block your credit card, Your current outstanding bill must be equal to zero.", "status_code": "204"},status=200)
                    profile=Profiles.objects.get(profile_id=profile_id)
                    profile.credit_card=credit_card_status
                    profile.save()

                customer.credit_card_status = credit_card_status

            customer.save()

            serializer = CreditcardsSerializer(customer)
            record = serializer.data
            return JsonResponse({"status_code":"200",'message':"record updated", 'record': record}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({"status_code": "400", 'message': 'No profile exists with the given profile id'},
                                status=200)

    if request.method == 'GET':
        credit_card_number = request.GET.get('credit_card_number', None)

        try:
            customer = Creditcards.objects.get(credit_card_number = credit_card_number)
            serializer = CreditcardsSerializer(customer)
            record = serializer.data
            return JsonResponse({"status_code": "200", 'record': record}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse(
                {'status_code': "400", 'message': 'No credit card exits with this number.'},
                status=200)


@csrf_exempt  # cross site request forgery
def debit_card_transaction(request=None):
    if request.method == 'POST':

        data = JSONParser().parse(request)
        debit_card_number = data.get('debit_card_number', None)

        destination_account_number = data.get('destination_account_number', None)
        debit_card_expiry_dates = data.get('debit_card_expiry_dates', None)
        debit_card_cvv = data.get('debit_card_cvv', None)
        debit_card_pin = data.get('debit_card_pin', None)
        transaction_amount = data.get('transaction_amount', None)

        try:
            customer_card_details = Debitcards.objects.get(debit_card_number=debit_card_number)
            source_account_number = customer_card_details.profile_id.account_number
            customer = Profiles.objects.get(account_number=source_account_number)
        except ObjectDoesNotExist:
            return JsonResponse({'status_code':"404",'message': 'No such debit card exist with this bank'}, status=200)

        if customer_card_details.debit_card_status=="Inactive":
            return JsonResponse(
                {'status_code': "201", 'message': 'Your debit card is in deactivated state please activate to do transactions'},
                status=200)

        elif (customer_card_details.debit_card_number == debit_card_number) and (customer_card_details.debit_card_status=='active')and(
                customer_card_details.debit_card_expiry_dates == debit_card_expiry_dates) and (
                customer_card_details.debit_card_cvv == debit_card_cvv) and (customer_card_details.debit_card_pin == debit_card_pin):

            if customer.account_balance:
                if (int(transaction_amount) > 0) and (int(transaction_amount) <= int(customer.account_balance)):
                    customer.account_balance = (int(customer.account_balance) - int(transaction_amount))
                    customer.save()

                    try:
                        destination_customer = Profiles.objects.get(account_number=destination_account_number)
                        destination_customer.account_balance = (int(destination_customer.account_balance) + int(transaction_amount))
                        destination_customer.save()

                    except ObjectDoesNotExist:
                        return JsonResponse(
                            {'status_code':"200",'message': 'destination_customer is not our bank customer', 'is_destination_found': True},
                            status=200)
                else:
                    return JsonResponse({'status_code': "404",
                                         'message': 'Invalid transaction amount or transaction amount exceeded your account balance'}, status=200)
            else:
                return JsonResponse({"status_code": "404", "message": "Insufficient funds"}, status=200)

            v = Debitcard_transactions(profile_id=customer, debit_card_number=debit_card_number, source_account_number=source_account_number,
                                       destination_account_number=destination_account_number,
                                       transaction_amount=transaction_amount)
            v.save()

            return JsonResponse({'status_code':"200",'message': "transaction successful"}, status=200)



        else:
            return JsonResponse({'status_code':"403",'message': " Invalid debit card details"}, status=200)


@csrf_exempt  # cross site request forgery
def debit_card_crud(request=None):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        account_number = data.get('account_number', None)

        key_list = ["account_number"]
        for key in key_list:
            if key not in data.keys():
                return JsonResponse({'message': " Missing mandatory field" + key, "status_code": "422"}, status=200)

        try:
            customer = Profiles.objects.get(account_number=account_number)
            if customer.debit_card == "Issued":
                return JsonResponse({'message': "customer has already taken debit card", "status_code": "409"},
                                    status=200)
            if customer.age >= 18:
                debit_card_number = debitcard_number_creation()
                debit_card_expiry_dates = card_expiry_calculator()
                debit_card_cvv = cvv_creation(3)
                v = Debitcards(profile_id=customer, debit_card_number=debit_card_number,
                               debit_card_cvv=debit_card_cvv, debit_card_expiry_dates=debit_card_expiry_dates)
                v.save()

                customer.debit_card = "Issued"
                customer.save()

                serializer = DebitcardsSerializer(v)
                record = serializer.data
                return JsonResponse({"status_code": "200", 'record': record}, status=200)

            else:
                return JsonResponse({"status_code": "204",
                                        'message': 'You are not eligible to get debit card as your age is not greater than or equal to 18'},
                                    status=200)

        except ObjectDoesNotExist:
            return JsonResponse({"status_code": "400",'message': 'You dont have any account with our bank'},
                                status=200)

    if request.method == 'PUT':
        data = JSONParser().parse(request)
        profile_id = data.get('profile_id', None)
        debit_card_pin = data.get('debit_card_pin', None)
        debit_card_status = data.get('debit_card_status', None)

        try:
            key_list = ["profile_id"]
            for key in key_list:
                if key not in data.keys():
                    return JsonResponse({'message': " Missing mandatory field " + key, "status_code": "422"},
                                        status=200)
            customer = Debitcards.objects.get(profile_id=profile_id)

            if debit_card_pin:
                customer.debit_card_pin = debit_card_pin

            if debit_card_status:
                if debit_card_status == "blocked":
                    profile = Profiles.objects.get(profile_id=profile_id)
                    profile.debit_card = debit_card_status
                    profile.save()
                customer.debit_card_status = debit_card_status

            customer.save()
            serializer = DebitcardsSerializer(customer)
            record = serializer.data
            return JsonResponse({"status_code": "200", "message": "record updated", "record": record}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse(
                {'status_code': "400", 'message': 'Invalid profile id'},
                status=200)

    if request.method == 'GET':
        debit_card_number = request.GET.get('debit_card_number', None)

        try:
            customer = Debitcards.objects.get(debit_card_number = debit_card_number)
            serializer = DebitcardsSerializer(customer)
            record = serializer.data
            return JsonResponse({"status_code": "200", 'record': record}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse(
                {'status_code': "400", 'message': 'No debit card exits with this number.'},
                status=200)


@csrf_exempt  # cross site request forgery
def profile_existence_check_on_aadhar_number(request=None):
    if request.method == 'GET':
        aadhar_number = request.GET.get('aadhar_number', None)
        try:
            customer = Profiles.objects.get(aadhar_number=aadhar_number)
            serializer = ProfilesSerializer(customer)
            record = serializer.data
            return JsonResponse({"status_code": "200", 'record': record}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'status_code': "404", 'message': "You don't have any account with our bank with the given aadhar number "+aadhar_number}, status=200)
        except Exception as e:
            return JsonResponse({"status_code": "400", "message": "Error in API code", "error": str(e)})
    else:
        return JsonResponse({"status_code": "500", "message": "Internal Server Error, due to incorrect Http request method"})


@csrf_exempt  # cross site request forgery
def profile_create(request=None):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        name = data.get('name', None)
        gender = data.get('gender', None)
        dob = data.get('dob', None)
        dob = dob_converter(dob)
        age = age_calculator(dob)
        mail_id = data.get('mail_id', None)
        phone_number = data.get('phone_number', None)
        occupation = data.get('occupation', None)
        address = data.get('address', None)
        aadhar_number = data.get("aadhar_number", None)
        pan_number = data.get('pan_number', None)
        account_balance = data.get('account_balance', None)
        account_number = account_number_creation()
        profile_id = profile_id_creation()

        key_list = ["name", "gender", "dob", "mail_id", "phone_number", "occupation","address", "aadhar_number", "pan_number"]
        for key in key_list:
            if key not in data.keys():
                return JsonResponse({'message': " Missing mandatory field " + key, "status_code": "422"}, status=200)

        # check whether any profile exists with the same aadhar number, if exists return error
        try:
            customer = Profiles.objects.get(aadhar_number=aadhar_number)
            return JsonResponse({"status_code": "409", 'message': "customer already exists"}, status=200)
        except ObjectDoesNotExist:
            pass

        try:
            customer = Profiles.objects.get(pan_number=pan_number)
            return JsonResponse({"status_code": "409", 'message': "A customer already exists with same pan number, "
                                                                  "pan number must be unique"}, status=200)
        except ObjectDoesNotExist:
            pass

        v = Profiles(name=name.lower(), gender=gender.lower(), dob=dob, age=age, phone_number=phone_number,
                     mail_id=mail_id.lower(),
                     address=address.lower(), occupation=occupation.lower(), aadhar_number=aadhar_number,
                     pan_number=pan_number,
                     account_number=account_number, account_balance=account_balance, profile_id=profile_id)
        v.save()
        # profile = Profiles.objects.get(v)
        serializer = ProfilesSerializer(v)
        record = serializer.data
        return JsonResponse({'status_code':"200",'message': record}, status=200)

    if request.method == 'PUT':
        data = JSONParser().parse(request)

        name = data.get('name', None)
        account_number = data.get('account_number', None)
        gender = data.get('gender', None)
        dob = data.get('dob', None)
        mail_id = data.get('mail_id', None)
        phone_number = data.get('phone_number', None)
        occupation = data.get('occupation', None)
        address = data.get('address', None)
        pan_number = data.get('pan_number', None)
        account_balance = data.get('account_balance', None)

        try:
            key_list = ["account_number"]
            for key in key_list:
                if key not in data.keys():
                    return JsonResponse({'message': " Missing mandatory field " + key, "status_code": "422"},
                                        status=200)
            customer = Profiles.objects.get(account_number=account_number)
            if name:
                customer.name = name
            if gender:
                customer.gender = gender

            if mail_id:
                customer.mail_id = mail_id
            if phone_number:
                customer.phone_number = phone_number
            if occupation:
                customer.occupation = occupation
            if address:
                customer.address = address
            if pan_number:
                customer.pan_number = pan_number
            if account_balance:
                customer.account_balance = int(customer.account_balance) + int(account_balance)

            customer.save()

            serializer = ProfilesSerializer(customer)
            record = serializer.data
            return JsonResponse({"status_code": "200",'message':"record updated", 'record': record}, status=200)


        except ObjectDoesNotExist:
            return JsonResponse({'status_code':"400",'message': 'Invalid account number'}, status=200)
    if request.method == 'GET':

        account_number = request.GET.get('account_number', None)

        try:
            customer = Profiles.objects.get(account_number=account_number)
            serializer = ProfilesSerializer(customer)
            record = serializer.data
            # get the debit card number and credit card number of that profile id
            profile_id = customer.profile_id
            try:
                creditcard_number = Creditcards.objects.get(profile_id=profile_id)
                record["creditcard_number"] = creditcard_number.credit_card_number
                debit_card_record = Debitcards.objects.only("debit_card_number").get(profile_id=profile_id)
                record["debit_card_number"] = debit_card_record.debit_card_number
            except ObjectDoesNotExist:
                pass
            return JsonResponse({"status_code": "200", 'record': record}, status=200)


        except ObjectDoesNotExist:
            return JsonResponse({'status_code':"400",'message': 'You dont have any account with our bank or Invalid account number'}, status=200)