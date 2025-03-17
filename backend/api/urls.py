"""URL configuration for the API application."""

from django.urls import path
from api.views.invoice import InvoiceUploadView, InvoicePreviewView
from api.views.auth import LoginView, LogoutView
from token_manager.views import fetch_account_details, get_transaction_history, ponto_login

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path(
        'invoices/upload/',
        InvoiceUploadView.as_view(),
        name='invoice-upload'
    ),
    path(
        'invoices/preview/<path:file_path>/',
        InvoicePreviewView.as_view(),
        name='invoice-preview'
    ),
    path('get-transactions-history/', get_transaction_history, name='transaction_history'),
    path('ponto-login/', ponto_login, name='ponto_login'),
    path('accounts/', fetch_account_details, name='accounts'),
]
