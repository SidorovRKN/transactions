from django.db import models

# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError

class Wallet(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.balance < 0:
            raise ValidationError("Баланс кошелька не может быть отрицательным.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    txid = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)

    def save(self, *args, **kwargs):
        # Проверяем, что обновление баланса не сделает его отрицательным
        new_balance = self.wallet.balance + self.amount
        if new_balance < 0:
            raise ValidationError("Баланс кошелька не может быть отрицательным после этой транзакции.")
        self.wallet.balance = new_balance
        self.wallet.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Корректируем баланс кошелька при удалении транзакции
        self.wallet.balance -= self.amount
        self.wallet.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.txid} for Wallet {self.wallet.label}"
