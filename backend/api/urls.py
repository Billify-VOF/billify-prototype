"""URL configuration for the API application."""

from django.urls import path
from api.views.invoice import InvoiceUploadView, InvoicePreviewView
from token_manager.views import ponto_login
from api.views.auth import LoginView, LogoutView

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
    path('ponto-login/', ponto_login, name='ponto_login'),
]
