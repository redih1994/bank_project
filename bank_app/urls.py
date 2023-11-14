# yourappname/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import BankerListClientsView, BankerRetrieveUpdateDestroyClientView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('banker/list-clients/', BankerListClientsView.as_view(), name='banker-list-clients'),
    path('banker/client/<int:pk>/', BankerRetrieveUpdateDestroyClientView.as_view(), name='banker-client-detail'),

]
