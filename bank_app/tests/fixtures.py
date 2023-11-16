import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from bank_app.models import CustomUser
from bank_app.serializers import CustomUserSerializer
from bank_app.permissions import IsBankerPermission

@pytest.fixture
def create_banker_user(django_db):
    # Create a banker user for testing
    banker_user = CustomUser.objects.create_user(
        username='banker_username',
        password='banker_password',
        is_banker=True
    )
    return banker_user