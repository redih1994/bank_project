from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from .permissions import IsBankerPermission

class BankerListClientsView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(is_client=True)
    serializer_class = CustomUserSerializer
    permission_classes = [IsBankerPermission]
