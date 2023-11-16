from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    is_banker = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class BankAccount(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='bank_account')
    account_id = models.CharField(max_length=255, unique=True)
    iban = models.CharField(max_length=255, unique=True)
    currency = models.CharField(max_length=3, default='EUR')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_approved = models.BooleanField(default=False)

class DebitCard(models.Model):
    card_number = models.CharField(max_length=16, unique=True)
    expiration_date = models.DateField()
    connected_account = models.OneToOneField(BankAccount, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

class DebitCardRequest(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

def generate_unique_transaction_id():
    return str(uuid.uuid4().hex)
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    )

    transaction_id = models.CharField(max_length=255, unique=True, default=generate_unique_transaction_id)
    bank_account = models.ForeignKey('BankAccount', on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_type}"