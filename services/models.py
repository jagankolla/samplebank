import uuid

from django.db import models
from datetime import datetime
# Create your models here.


class Netbanking(models.Model):
    profile_id = models.ForeignKey('Profiles', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=50, unique=True, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    net_banking_status = models.CharField(max_length=10, default='active', blank=True)
    created_on = models.DateTimeField(default=datetime.now)
    last_updated_on = models.DateTimeField(auto_now=True)


class Netbanking_transaction(models.Model):
    profile_id = models.ForeignKey('Profiles', on_delete=models.CASCADE)
    source_account_number = models.CharField(max_length=50, null=True, blank=True)
    destination_account_number = models.CharField(max_length=50, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, default="Netbanking", blank=True)
    transaction_amount = models.CharField(max_length=50, null=True, blank=True)
    transaction_time = models.DateTimeField(auto_now=True)


class Creditcards(models.Model):
    profile_id = models.ForeignKey('Profiles', on_delete=models.CASCADE)
    credit_card_number = models.CharField(max_length=50, null=True, blank=True)
    credit_card_expiry_dates = models.CharField(max_length=50, null=True, blank=True)
    credit_card_cvv = models.CharField(max_length=3, null=True, blank=True)
    credit_card_limit = models.CharField(max_length=6, null=True, blank=True)
    available_credit_card_limit = models.CharField(max_length=6, null=True, blank=True)
    current_outstanding_bill = models.CharField(max_length=6, default="0")
    credit_card_pin = models.CharField(max_length=6, null=True, blank=True)
    credit_card_status = models.CharField(max_length=10, default="active")
    created_on = models.DateTimeField(default=datetime.now)
    last_updated_on = models.DateTimeField(auto_now=True)


class Creditcard_transactions(models.Model):
    profile_id = models.ForeignKey('Profiles', on_delete=models.CASCADE)
    credit_card_number = models.CharField(max_length=50, null=True, blank=True)
    transaction_category = models.CharField(max_length=50, default="others")
    transaction_amount = models.CharField(max_length=50, null=True, blank=True)
    transaction_time = models.DateTimeField(auto_now=True)


class Debitcards(models.Model):
    profile_id = models.ForeignKey('Profiles', on_delete=models.CASCADE)
    debit_card_number = models.CharField(max_length=50, null=True, blank=True)
    debit_card_expiry_dates = models.CharField(max_length=50, null=True, blank=True)
    debit_card_cvv = models.CharField(max_length=3, null=True, blank=True)
    debit_card_pin = models.CharField(max_length=6, null=True, blank=True)
    debit_card_status = models.CharField(max_length=10, default="active", blank=True)
    created_on = models.DateTimeField(default=datetime.now)
    last_updated_on = models.DateTimeField(auto_now=True)


class Debitcard_transactions(models.Model):
    profile_id = models.ForeignKey('Profiles', on_delete=models.CASCADE)
    source_account_number = models.CharField(max_length=50, null=True, blank=True)
    destination_account_number = models.CharField(max_length=50, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, default="Debit Card", blank=True)
    debit_card_number = models.CharField(max_length=50, null=True, blank=True)
    transaction_amount = models.CharField(max_length=50, null=True, blank=True)
    transaction_time = models.DateTimeField(auto_now=True)


class Profiles(models.Model):
    profile_id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    dob = models.DateTimeField(default=datetime.now)
    age = models.IntegerField(blank=False, null=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    mail_id = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    occupation = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    pan_number = models.CharField(max_length=150, null=True, blank=True, unique=True)
    aadhar_number = models.CharField(max_length=50, null=True, blank=True, unique=True)
    account_number = models.CharField(max_length=50, null=True, blank=True, unique=True)
    account_balance = models.CharField(max_length=50, null=True, blank=True)
    debit_card = models.CharField(max_length=50, default="Not Issued", blank=True)
    credit_card = models.CharField(max_length=50, default="Not Issued", blank=True)
    net_banking = models.CharField(max_length=50, default="Not Issued", blank=True)
    created_on= models.DateTimeField(default=datetime.now)
    last_updated_on= models.DateTimeField(auto_now=True)
