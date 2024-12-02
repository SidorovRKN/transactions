import uuid

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
    source_wallet = models.ForeignKey(
        'Wallet',
        related_name='outgoing_transactions',
        on_delete=models.CASCADE,
        null=True,  # null для случая, если транзакция только начисляет средства
        blank=True
    )
    destination_wallet = models.ForeignKey(
        'Wallet',
        related_name='incoming_transactions',
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    txid = models.CharField(unique=True, max_length=40)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_wallet} -> {self.destination_wallet} : {self.amount}"

    def save(self, *args, **kwargs):
        self.txid = uuid.uuid4()
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """
        Проверка: сумма должна быть положительной и баланс источника достаточен.
        """
        if self.source_wallet and self.source_wallet.balance < self.amount:
            raise ValidationError("Недостаточно средств на исходном кошельке")
        if self.amount <= 0:
            raise ValidationError("Сумма должна быть больше нуля")
