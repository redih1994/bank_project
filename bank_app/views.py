from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from .permissions import IsBankerPermission
from .models import BankAccount
from .serializers import BankAccountRequestSerializer, BankAccountSerializer
from .permissions import IsClientPermission
import uuid


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
        # Optionally, you can add custom logic for delete, e.g., archive instead of hard delete
        return self.destroy(request, *args, **kwargs)