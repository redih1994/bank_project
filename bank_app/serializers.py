from rest_framework import serializers
from .models import CustomUser
from .models import BankAccount, DebitCard, DebitCardRequest, Transaction

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_client']


class BankAccountRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['account_id', 'iban', 'currency']
        read_only_fields = ['account_id', 'iban']

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

class DebitCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitCard
        fields = '__all__'

class DebitCardRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitCardRequest
        fields = ['id', 'monthly_salary', 'is_approved', 'rejection_reason', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['bank_account', 'amount', 'currency', 'transaction_type', 'created_at']
        read_only_fields = ['transaction_id', 'created_at']
