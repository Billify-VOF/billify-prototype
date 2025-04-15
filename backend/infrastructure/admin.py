from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.auth.admin import UserAdmin
from infrastructure.django.models.account import Account
from infrastructure.django.models.invoice import Invoice
import logging

# Configure logger
logger = logging.getLogger(__name__)


@admin.register(Account)
class AccountAdmin(UserAdmin):
    """
    Register CustomUser model in the Django admin.
    """

    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Register Invoice model in the Django admin.
    """

    list_display = ("invoice_number", "total_amount", "status", "due_date")
    search_fields = ("invoice_number", "original_file_name")


# Check if the default User model is registered before trying to unregister it
try:
    from django.contrib.auth.models import User

    admin.site.unregister(User)
except NotRegistered:
    logger.debug("Default User model was not registered in admin")
except Exception as e:
    logger.warning(f"Unexpected error when unregistering User model: {str(e)}")
