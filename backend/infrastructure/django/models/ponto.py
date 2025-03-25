from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class IbanityAccount(models.Model):
    """
    IbanityAccount Model which represents the account info used in
    Ponto-Connect.
    """

    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    account_id: models.CharField = models.CharField(
        max_length=255, unique=True
    )
    description: models.CharField = models.CharField(
        max_length=255, blank=True
    )
    product: models.CharField = models.CharField(max_length=255, blank=True)
    reference: models.CharField = models.CharField(max_length=255, blank=True)
    currency: models.CharField = models.CharField(max_length=10, blank=True)
    authorization_expiration_expected_at: models.DateTimeField = (
        models.DateTimeField(null=True, blank=True)
    )
    current_balance: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    available_balance: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    subtype: models.CharField = models.CharField(max_length=255, blank=True)
    holder_name: models.CharField = models.CharField(
        max_length=255, blank=True
    )
    resource_id: models.CharField = models.CharField(
        max_length=255, blank=True
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ibanity Account"
        verbose_name_plural = "Ibanity Accounts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.account_id} - {self.description}"


class PontoToken(models.Model):
    """
    Stores Ponto access token used in Ponto Connect for API access.
    """

    user: models.OneToOneField = models.OneToOneField(
        User, on_delete=models.CASCADE
    )
    access_token: models.CharField = models.CharField(
        max_length=255, null=True, blank=True, unique=True
    )
    refresh_token: models.CharField = models.CharField(
        max_length=255, null=True, blank=True, unique=True
    )
    expires_in: models.IntegerField = models.IntegerField(
        default=3600, null=True, blank=True
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ponto Token"
        verbose_name_plural = "Ponto Tokens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ponto Token for {self.user.username}"
