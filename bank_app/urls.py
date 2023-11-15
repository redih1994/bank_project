# yourappname/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    BankerListClientsView,
    BankerRetrieveUpdateDestroyClientView,
    ClientRequestBankAccountView,
    ClientRetrieveBankAccountView,
    BankerListBankAccountsView,
    BankerRetrieveUpdateDestroyBankAccountView,
    BankerCreateClientView,
    ClientRequestDebitCardView,
    BankerListDebitCardRequestsView,
    BankerReviewDebitCardRequestView,
    ClientDebitCardRequestInfo,
    ClientDebitCardView
)
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('banker/list-clients/', BankerListClientsView.as_view(), name='banker-list-clients'),
    path('banker/client/<int:pk>/', BankerRetrieveUpdateDestroyClientView.as_view(), name='banker-client-detail'),
    path('banker/client/create/', BankerCreateClientView.as_view(), name='banker-client-create'),
    path('client/request-bank-account/', ClientRequestBankAccountView.as_view(), name='client-request-bank-account'),
    path('client/retrieve-bank-account/', ClientRetrieveBankAccountView.as_view(), name='client-retrieve-bank-account'),
    path('banker/list-bank-accounts/', BankerListBankAccountsView.as_view(), name='banker-list-bank-accounts'),
    path('banker/bank-accounts/<int:pk>/', BankerRetrieveUpdateDestroyBankAccountView.as_view(), name='banker-bank-account-detail'),
    path('client/request-debit-card/', ClientRequestDebitCardView.as_view(), name='client-request-debit-card'),
    path('client/debit-card-request-info/', ClientDebitCardRequestInfo.as_view(), name='client-debit-card-requests'),
    path('banker/list-debit-card-requests/', BankerListDebitCardRequestsView.as_view(), name='banker-list-debit-card-requests'),
    path('banker/review-debit-card-request/<int:pk>/', BankerReviewDebitCardRequestView.as_view(), name='banker-review-debit-card-request'),
    path('client/debit-cards/', ClientDebitCardView.as_view(), name='client-debit-cards'),

]
