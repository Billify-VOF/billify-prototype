from django.db import models

# Create your models here.


# class BankAccount(models.Model):
#     account_id = models.CharField(max_length=255, unique=True)
#     balance = models.DecimalField(max_digits=12, decimal_places=2)
#     currency = models.CharField(max_length=10)
#     last_updated = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Account {self.account_id} - {self.balance} {self.currency}"


# class Transaction(models.Model):
#     transaction_id = models.CharField(max_length=255, unique=True)
#     account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     currency = models.CharField(max_length=10)
#     description = models.TextField()
#     date = models.DateTimeField()

#     def __str__(self):
#         return f"Transaction {self.transaction_id} - {self.amount} {self.currency}"