from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from .permissions import IsBankerPermission

class BankerListClientsView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(is_client=True)
    serializer_class = CustomUserSerializer
    permission_classes = [IsBankerPermission]

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