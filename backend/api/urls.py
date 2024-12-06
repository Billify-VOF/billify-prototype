"""URL configuration for the API application."""

from django.urls import path
from api.views.invoice import InvoiceUploadView

urlpatterns = [
    path(
        'invoices/upload/',
        InvoiceUploadView.as_view(),
        name='invoice-upload'
    ),
]
