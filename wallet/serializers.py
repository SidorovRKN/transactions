from rest_framework import serializers
from .models import Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'label', 'balance']


from rest_framework import serializers

class TransactionSerializer(serializers.ModelSerializer):
    txid = serializers.CharField(read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'source_wallet', 'destination_wallet', 'amount', 'timestamp', "txid"]

    def validate(self, data):
        """
        Дополнительные проверки.
        """
        if data['source_wallet'] == data['destination_wallet']:
            raise serializers.ValidationError("Источник и назначение транзакции не могут совпадать.")
        if data['amount'] <= 0:
            raise serializers.ValidationError("Сумма должна быть больше нуля.")
        if data['source_wallet'] and data['source_wallet'].balance < data['amount']:
            raise serializers.ValidationError("Недостаточно средств на исходном кошельке.")
        return data
