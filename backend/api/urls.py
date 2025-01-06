"""URL configuration for the API application."""

from django.urls import path
from api.views.invoice import InvoiceUploadView, InvoicePreviewView

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
]
