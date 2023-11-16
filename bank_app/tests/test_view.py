import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from bank_app.models import CustomUser, BankAccount, DebitCard
from bank_app.serializers import CustomUserSerializer
from bank_app.serializers import BankAccountSerializer, DebitCardSerializer


@pytest.fixture
def create_banker_user(django_db_setup):
    # Create a banker user for testing
    banker_user = CustomUser.objects.create_user(
        username='banker_username',
        password='banker_password',
        is_banker=True
    )
    return banker_user


@pytest.fixture
def create_client_user(django_db_setup):
    # Create a client user for testing
    client_user = CustomUser.objects.create_user(
        username='client_username',
        password='client_password',
        is_client=True
    )
    return client_user


@pytest.fixture
def create_debit_card(create_client_user, django_db_setup):
    # Create a debit card for a client user
    bank_account = BankAccount.objects.create(
        user=create_client_user,
        account_id='ACCT_12345678',
        iban='IBAN_abcdefgh123',
        currency='EUR',
        balance=0.00,
        is_approved=True
    )

    debit_card = DebitCard.objects.create(
        card_number='1234567890123456',
        expiration_date='2023-12-31',
        connected_account=bank_account,
        is_approved=True
    )
    return debit_card


@pytest.mark.django_db
class TestBankerCreateClientView:

    def test_create_client_success(self, create_banker_user):
        # Log in the banker user
        client = APIClient()
        client.force_authenticate(user=create_banker_user)

        url = reverse('banker-client-create')
        data = {'username': 'test_client', 'password': 'test_password', 'is_client': True}
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

        created_user = CustomUser.objects.get(username='test_client')
        expected_data = CustomUserSerializer(created_user).data
        assert response.data == expected_data

        assert created_user.is_client is True

    def test_create_client_invalid_data(self, create_banker_user):
        # Log in the banker user
        client = APIClient()
        client.force_authenticate(user=create_banker_user)

        url = reverse('banker-client-create')
        data = {'username': '', 'password': 'test_password', 'is_client': True}
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert 'username' in response.data

    def test_create_client_unauthorized(self):
        regular_user = CustomUser.objects.create_user(
            username='regular_user',
            password='regular_password',
            is_client=True
        )

        # Log in the regular user
        client = APIClient()
        client.force_authenticate(user=regular_user)

        # Make a request to the view with valid data
        url = reverse('banker-client-create')
        data = {'username': 'test_client', 'password': 'test_password', 'is_client': True}
        response = client.post(url, data, format='json')

        # Check the response status code
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.fixture
def create_bank_account(create_client_user, django_db_setup):
    # Create a bank account for a client user
    bank_account = BankAccount.objects.create(
        user=create_client_user,
        account_id='ACCT_12345678',
        iban='IBAN_abcdefgh123',
        currency='EUR',
        balance=0.00,
        is_approved=True
    )
    return bank_account


@pytest.mark.django_db
class TestClientRequestBankAccountView:

    def test_create_bank_account_success(self, create_client_user):
        # Log in the client user
        client = APIClient()
        client.force_authenticate(user=create_client_user)

        url = reverse('client-request-bank-account')
        response = client.post(url, data={}, format='json')

        assert response.status_code == status.HTTP_201_CREATED

        assert BankAccount.objects.filter(user=create_client_user).exists()

    def test_unauthorized_access(self):
        # Create a regular user (non-client)
        regular_user = CustomUser.objects.create_user(
            username='regular_user',
            password='regular_password',
            is_client=False
        )

        client = APIClient()
        client.force_authenticate(user=regular_user)

        url = reverse('client-request-bank-account')
        response = client.post(url, data={}, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestClientRetrieveBankAccountView:

    def test_retrieve_bank_account_success(self, create_client_user, create_bank_account):
        # Log in the client user
        client = APIClient()
        client.force_authenticate(user=create_client_user)

        url = reverse('client-retrieve-bank-account')
        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK

        expected_data = BankAccountSerializer(create_bank_account).data
        assert response.data == expected_data

    def test_unauthenticated_access(self):
        # Create a client user for testing
        client_user = CustomUser.objects.create_user(
            username='client_username',
            password='client_password',
            is_client=True
        )

        client = APIClient()
        client.force_authenticate(user=client_user)

        url = reverse('client-retrieve-bank-account')
        client.logout()
        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthorized_access(self, create_client_user):
        # Log in a regular user
        regular_user = CustomUser.objects.create_user(
            username='regular_user',
            password='regular_password',
            is_client=False
        )

        client = APIClient()
        client.force_authenticate(user=regular_user)

        url = reverse('client-retrieve-bank-account')
        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestClientDebitCardView:

    def test_list_debit_cards_success(self, create_client_user, create_debit_card):
        # Log in the client user
        client = APIClient()
        client.force_authenticate(user=create_client_user)

        url = reverse('client-debit-cards')
        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK

        expected_data = DebitCardSerializer([create_debit_card], many=True).data
        assert response.data == expected_data

    def test_unauthenticated_access(self):
        # Create a client user for testing
        client_user = CustomUser.objects.create_user(
            username='client_username',
            password='client_password',
            is_client=True
        )


        client = APIClient()
        client.force_authenticate(user=client_user)


        url = reverse('client-debit-cards')
        client.logout()
        response = client.get(url, format='json')


        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthorized_access(self, create_client_user):
        # Log in a regular user (non-client)
        regular_user = CustomUser.objects.create_user(
            username='regular_user',
            password='regular_password',
            is_client=False
        )

        client = APIClient()
        client.force_authenticate(user=regular_user)

        url = reverse('client-debit-cards')
        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
