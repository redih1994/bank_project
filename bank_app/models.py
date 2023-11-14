from django.contrib.auth.models import AbstractUser
from django.db import models

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