from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class Account(AbstractUser):
    """Custom user model extending Django's AbstractUser."""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name="account_set",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="account_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
    )

    class Meta:
        app_label = "infrastructure"
