from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from infrastructure.django.models.account import Account


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
except Exception:
    pass  # Do nothing if User model is not registered
