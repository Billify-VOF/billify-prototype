from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class IbanityAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_id = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)
    product = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    authorization_expiration_expected_at = models.DateTimeField(null=True, blank=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    subtype = models.CharField(max_length=255, blank=True)
    holder_name = models.CharField(max_length=255, blank=True)
    resource_id = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return f"{self.account_id} - {self.description}"


class PontoToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, null=True, blank=True,unique=True)
    refresh_token = models.CharField(max_length=255, null=True, blank=True,unique=True)#add unique true
    expires_in = models.IntegerField(default=3600)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ponto Token for {self.user.username}"

