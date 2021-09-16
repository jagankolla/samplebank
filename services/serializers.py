from rest_framework import serializers
from .models import Profiles, Debitcards, Creditcards, Netbanking, Netbanking_transaction, Debitcard_transactions, \
    Creditcard_transactions


class ProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profiles
        fields = '__all__'


class DebitcardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debitcards
        exclude = ('id',)


class CreditcardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creditcards
        exclude = ('id',)


class NetbankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Netbanking
        exclude = ('id',)


class NetBankingTxnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Netbanking_transaction
        fields = '__all__'


class DebitcardTxnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debitcard_transactions
        fields = '__all__'


class CreditcardTxnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creditcard_transactions
        fields = '__all__'


class CreditcardTxnReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creditcard_transactions
        fields = ('transaction_category',)


class CategoryWiseCreditcardTxnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creditcard_transactions
        fields = ('transaction_amount', 'transaction_time',)
