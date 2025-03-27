"""URL configuration for the API application."""

from django.urls import path
from api.views.auth import LoginView, LogoutView
from api.views.invoice import InvoiceUploadView, InvoicePreviewView
from api.views.ponto import PontoView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("invoices/upload/", InvoiceUploadView.as_view(), name="invoice-upload"),
    path("invoices/preview/<path:file_path>/", InvoicePreviewView.as_view(), name="invoice-preview"),
    path(
        "ponto/transactions-history/",
        PontoView.as_view(),
        {"action": "get_transaction_history"},
        name="transaction_history",
    ),
    path("ponto/login/", PontoView.as_view(), {"action": "ponto_login"}, name="ponto_login"),
    path(
        "ponto/login/refresh/",
        PontoView.as_view(),
        {"action": "refresh_access_token"},
        name="ponto_login_refresh",
    ),
    path("ponto/accounts/", PontoView.as_view(), {"action": "fetch_account_details"}, name="accounts"),
]
