from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from .permissions import IsBankerPermission
from .models import BankAccount, DebitCard, DebitCardRequest, Transaction
from .serializers import BankAccountRequestSerializer, BankAccountSerializer, DebitCardSerializer, \
    DebitCardRequestSerializer, TransactionSerializer
from .permissions import IsClientPermission
import uuid
from rest_framework import serializers
from decimal import Decimal


class BankerListClientsView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(is_client=True)
    serializer_class = CustomUserSerializer
    permission_classes = [IsBankerPermission]


class BankerCreateClientView(generics.CreateAPIView):
    queryset = CustomUser.objects.filter(is_client=True)
    serializer_class = CustomUserSerializer
    permission_classes = [IsBankerPermission]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BankerRetrieveUpdateDestroyClientView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.filter(is_client=True)
    serializer_class = CustomUserSerializer
    permission_classes = [IsBankerPermission]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class ClientRequestBankAccountView(generics.CreateAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountRequestSerializer
    permission_classes = [IsClientPermission]

    def perform_create(self, serializer):
        existing_account = BankAccount.objects.filter(user=self.request.user)

        if existing_account:
            raise serializers.ValidationError("You already have a bank account.")

        account_id = generate_unique_account_id()
        iban = generate_unique_iban()

        serializer.save(user=self.request.user, account_id=account_id, iban=iban)
        return Response({'detail': 'Bank account request submitted for approval.'}, status=status.HTTP_201_CREATED)


def generate_unique_account_id():
    return 'ACCT_' + str(uuid.uuid4().hex)[:8]


def generate_unique_iban():
    return 'IBAN_' + str(uuid.uuid4().hex)[:12]


class ClientRetrieveBankAccountView(generics.RetrieveAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [IsClientPermission]

    def get_object(self):
        return BankAccount.objects.get(user=self.request.user)


class BankerListBankAccountsView(generics.ListAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsBankerPermission]


class BankerRetrieveUpdateDestroyBankAccountView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsBankerPermission]

    def perform_update(self, serializer):
        serializer.save(is_approved=True)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ClientRequestDebitCardView(generics.CreateAPIView):
    queryset = DebitCardRequest.objects.all()
    serializer_class = DebitCardRequestSerializer
    permission_classes = [IsClientPermission]

    def perform_create(self, serializer):
        client = self.request.user

        existing_request = DebitCardRequest.objects.filter(client=client, is_approved=False).first()
        if existing_request:
            raise serializers.ValidationError("You have already made a debit card request. Please wait for approval.")

        # Check if the associated bank account is approved
        bank_account = BankAccount.objects.get(user=client)
        if not bank_account.is_approved:
            raise serializers.ValidationError("Bank account must be approved to request a debit card.")

        # Check if a debit card is already connected to the account
        existing_debit_card = DebitCard.objects.filter(connected_account=bank_account).first()
        if existing_debit_card:
            raise serializers.ValidationError("A debit card is already connected to this account.")

        # Check if the client's salary is less than 500 euros
        salary = serializer.validated_data.get('monthly_salary', 0)
        if salary < 500:
            raise serializers.ValidationError("Salary must be at least 500 euros to request a debit card.")

        serializer.save(client=client)

        return Response({'detail': 'Debit card request submitted for approval.'}, status=status.HTTP_201_CREATED)


class ClientDebitCardRequestInfo(generics.ListAPIView):
    serializer_class = DebitCardRequestSerializer
    permission_classes = [IsClientPermission]

    def get_queryset(self):
        # Retrieve the debit card requests for the authenticated client
        client = self.request.user
        return DebitCardRequest.objects.filter(client=client)


class BankerReviewDebitCardRequestView(generics.RetrieveUpdateAPIView):
    queryset = DebitCardRequest.objects.all()
    serializer_class = DebitCardRequestSerializer
    permission_classes = [IsBankerPermission]

    def perform_update(self, serializer):
        # Retrieve the existing instance
        instance = self.get_object()

        # If the request is approved, create a new DebitCard instance
        if serializer.validated_data.get('is_approved', False):
            client = instance.client
            bank_account = BankAccount.objects.get(user=client)

            card_number = generate_unique_card_number()

            # Create the DebitCard instance
            DebitCard.objects.create(
                card_number=card_number,
                expiration_date=calculate_expiration_date(),
                connected_account=bank_account,
                is_approved=True
            )

        serializer.save()


def generate_unique_card_number():
    return 'CARD_' + str(uuid.uuid4().hex)[:10]


def calculate_expiration_date():
    return timezone.now() + timedelta(days=365)


class BankerListDebitCardRequestsView(generics.ListAPIView):
    queryset = DebitCardRequest.objects.filter(is_approved=False)
    serializer_class = DebitCardRequestSerializer
    permission_classes = [IsBankerPermission]

class BankerListDebitCardsView(generics.ListAPIView):
    queryset = DebitCard.objects.all()
    serializer_class = DebitCardSerializer
    permission_classes = [IsBankerPermission]


class ClientDebitCardView(generics.ListAPIView):
    serializer_class = DebitCardSerializer
    permission_classes = [IsClientPermission]

    def get_queryset(self):
        # Retrieve the credit cards for the authenticated client
        client = self.request.user
        return DebitCard.objects.filter(connected_account__user=client)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Check if the queryset is empty
        if not queryset.exists():
            raise serializers.ValidationError("You do not have a debit card or it is not approved by the banker.")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TransactionCreateView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsClientPermission]

    def create(self, request, *args, **kwargs):
        # Retrieve the authenticated client
        client = request.user

        # Retrieve request data
        receiver_iban = request.data.get('receiver_iban', None)
        amount = request.data.get('amount', None)

        # Validate request data
        if not receiver_iban or not amount:
            return Response({"detail": "Receiver IBAN and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve sender's bank account
            sender_account = BankAccount.objects.get(user=client)
            if not DebitCard.objects.filter(connected_account=sender_account, is_approved=True).exists():
                return Response({"detail": "You must have an approved debit card to perform a transaction."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Retrieve receiver's bank account
            receiver_account = BankAccount.objects.get(iban=receiver_iban)
            if not DebitCard.objects.filter(connected_account=receiver_account, is_approved=True).exists():
                return Response({"detail": "The receiver must have an approved debit card to perform a transaction."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if there's enough balance in the sender's account
            if sender_account.balance < float(amount):
                return Response({"detail": "Insufficient balance in the sender's account."},
                                status=status.HTTP_400_BAD_REQUEST)
            sender_account.balance -= Decimal(amount)
            receiver_account.balance += Decimal(amount)
            sender_account.save()
            receiver_account.save()
            # Perform the transaction
            Transaction.objects.create(
                bank_account=sender_account,
                amount=amount,
                currency="EUR",
                transaction_type="DEBIT"
            )
            # Create a credit transaction for the receiver's account
            Transaction.objects.create(
                bank_account=receiver_account,
                amount=amount,
                currency="EUR",
                transaction_type="CREDIT"
            )
            # Update the sender's account balance

            return Response({"The Transaction is successful"}, status=status.HTTP_201_CREATED)

        except BankAccount.DoesNotExist:
            return Response({"detail": "Invalid receiver IBAN."}, status=status.HTTP_400_BAD_REQUEST)


class ClientTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsClientPermission]

    def get_queryset(self):
        # Retrieve the authenticated client
        client = self.request.user

        # Retrieve transactions for the authenticated client
        return Transaction.objects.filter(bank_account__user=client)


class BankerTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsBankerPermission]

    def get_queryset(self):
        # Retrieve all transactions for the banker
        return Transaction.objects.all()


class WithdrawalCreateView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsClientPermission]

    def create(self, request, *args, **kwargs):
        # Retrieve the authenticated client
        client = request.user

        # Retrieve request data
        amount = request.data.get('amount', None)

        # Validate request data
        if not amount:
            return Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve sender's bank account
            sender_account = BankAccount.objects.get(user=client)

            # Check if the sender has a debit card
            if not DebitCard.objects.filter(connected_account=sender_account, is_approved=True).exists():
                return Response({"detail": "You must have an approved debit card to perform a withdrawal."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if there's enough balance in the sender's account
            if sender_account.balance < float(amount):
                return Response({"detail": "Insufficient balance in the sender's account."},
                                status=status.HTTP_400_BAD_REQUEST)

            sender_account.balance -= Decimal(amount)
            sender_account.save()

            # Perform the withdrawal transaction
            Transaction.objects.create(
                bank_account=sender_account,
                amount=amount,
                currency="EUR",
                transaction_type="DEBIT",
            )

            return Response({"detail": "Withdrawal is successful"}, status=status.HTTP_201_CREATED)

        except BankAccount.DoesNotExist:
            return Response({"detail": "Invalid bank account."}, status=status.HTTP_400_BAD_REQUEST)


class DepositCreateView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsClientPermission]

    def create(self, request, *args, **kwargs):
        # Retrieve the authenticated client
        client = request.user

        # Retrieve request data
        amount = request.data.get('amount', None)

        # Validate request data
        if not amount:
            return Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve sender's bank account
            sender_account = BankAccount.objects.get(user=client)

            # Check if the sender has a debit card
            if not DebitCard.objects.filter(connected_account=sender_account, is_approved=True).exists():
                return Response({"detail": "You must have an approved debit card to perform a deposit."},
                                status=status.HTTP_400_BAD_REQUEST)

            sender_account.balance += Decimal(amount)
            sender_account.save()

            # Perform the deposit transaction
            Transaction.objects.create(
                bank_account=sender_account,
                amount=amount,
                currency="EUR",
                transaction_type="CREDIT",
            )

            return Response({"detail": "Deposit is successful"}, status=status.HTTP_201_CREATED)

        except BankAccount.DoesNotExist:
            return Response({"detail": "Invalid bank account."}, status=status.HTTP_400_BAD_REQUEST)


