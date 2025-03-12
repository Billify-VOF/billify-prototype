from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PontoToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, null=True, blank=True,unique=True)
    refresh_token = models.CharField(max_length=255, null=True, blank=True,unique=True)
    expires_in = models.IntegerField(default=3600)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ponto Token for {self.user.username}"