from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model that extends Django's AbstractUser."""

    company_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    class Meta:
        db_table = "auth_user"
        swappable = "AUTH_USER_MODEL"
