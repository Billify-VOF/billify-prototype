"""URL configuration for the API application."""

from django.urls import path
from api.views.invoice import InvoiceUploadView, InvoicePreviewView
from token_manager.views import ponto_login,ponto_callback

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
    path('ponto/callback/', ponto_callback, name='ponto_callback'),
    

]
