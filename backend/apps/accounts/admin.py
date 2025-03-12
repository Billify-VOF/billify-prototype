from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

# Get the custom user model dynamically
CustomUser = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Register CustomUser model in the Django admin.
    """
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

# Check if the default User model is registered before trying to unregister it
try:
    from django.contrib.auth.models import User
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass  # Do nothing if User model is not registered
