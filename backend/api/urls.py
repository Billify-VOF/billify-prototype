"""URL configuration for the API application."""

from django.urls import path
from api.views.invoice import InvoiceUploadView, InvoicePreviewView
from token_manager.views import ponto_login,fetch_account_details,get_transaction_history,Create_Payment

urlpatterns = [
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
    path('ponto-login/', ponto_login, name='ponto_login'),
    path('accounts/', fetch_account_details, name='accounts'),
    path('get-transactions-history/', get_transaction_history, name='transaction_history'),
    path('create-payments/', Create_Payment, name='payment-create'),
    
    

]
