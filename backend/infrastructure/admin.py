from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.auth.admin import UserAdmin
from infrastructure.django.models.account import Account
import logging

# Configure logger
logger = logging.getLogger(__name__)


@admin.register(Account)
class AccountAdmin(UserAdmin):
    """
    Register CustomUser model in the Django admin.
    """
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


# Check if the default User model is registered before trying to unregister it
try:
    from django.contrib.auth.models import User
    admin.site.unregister(User)
except NotRegistered:
    logger.debug("Default User model was not registered in admin")
except Exception as e:
    logger.warning(f"Unexpected error when unregistering User model: {str(e)}")
