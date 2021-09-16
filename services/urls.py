from django.urls import path

from . import views

urlpatterns = [
    path('profiles', views.profile_create),
    path('debit-card', views.debit_card_crud),
    path('credit-card', views.credit_card_crud),
    path('net-banking', views.net_banking_crud),
    path('credit-card-txn', views.credit_card_transaction),
    path('debit-card-txn', views.debit_card_transaction),
    path('net-banking-txn', views.net_banking_transaction),
    path('account-txn', views.account_transaction),
    path('login', views.login),
    path('spend-analyzer', views.spend_analyzer),
    path("profile-existence", views.profile_existence_check_on_aadhar_number),
]