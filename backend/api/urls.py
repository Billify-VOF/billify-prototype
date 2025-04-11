"""URL configuration for the API application.

This module defines all the API endpoints for the Billify application,
organizing them into logical groups by feature area. It maps URLs to view
classes that handle API requests and responses.

URL patterns are organized by feature:
- Authentication endpoints (/auth/*)
- Invoice endpoints (/invoices/*)
- Ponto integration endpoints (/ponto/*)
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from api.views.invoice import InvoiceUploadView, InvoicePreviewView, InvoiceConfirmationView, InvoiceViewSet
from api.views.auth import LoginView, LogoutView, RegisterView, get_user_profile
from api.views.ponto import PontoView

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", get_user_profile, name="user-profile"),
    path("invoices/upload/", InvoiceUploadView.as_view(), name="invoice-upload"),
    # Invoice confirmation endpoint - handles the second phase of the two-phase storage approach
    # Transfers files from temporary to permanent storage after user review
    path(
        "invoices/<int:invoice_id>/confirm/",
        InvoiceConfirmationView.as_view(),
        name="invoice-confirm",
    ),
    path(
        "invoices/preview/<path:file_path>/",
        InvoicePreviewView.as_view(),
        name="invoice-preview",
    ),
    path(
        "ponto/transactions-history/",
        PontoView.as_view(),
        {"action": "get_transaction_history"},
        name="transaction_history",
    ),
    path(
        "ponto/login/",
        PontoView.as_view(),
        {"action": "ponto_login"},
        name="ponto_login",
    ),
    path(
        "ponto/login/refresh/",
        PontoView.as_view(),
        {"action": "refresh_access_token"},
        name="ponto_login_refresh",
    ),
    path(
        "ponto/accounts/",
        PontoView.as_view(),
        {"action": "fetch_account_details"},
        name="accounts",
    ),
]

urlpatterns += router.urls
