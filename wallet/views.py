from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# Wallet List View
class WalletListView(ListCreateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['label']  # Фильтрация по label
    ordering_fields = ['balance']  # Сортировка по balance
    ordering = ['balance']  # Сортировка по умолчанию (asc)


# Wallet Detail View
class WalletDetailView(RetrieveDestroyAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


# Transaction List View
from rest_framework.exceptions import ValidationError
from django.db import transaction  # Для управления транзакциями базы данных

class TransactionListView(ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        """
        Создаёт транзакцию и обновляет балансы кошельков.
        """
        source_wallet = serializer.validated_data.get('source_wallet')
        destination_wallet = serializer.validated_data['destination_wallet']
        amount = serializer.validated_data['amount']

        if source_wallet and source_wallet.balance < amount:
            raise ValidationError("Недостаточно средств на исходном кошельке.")

        # Атомарная операция для безопасности
        with transaction.atomic():
            # Списание средств
            if source_wallet:
                source_wallet.balance -= amount
                source_wallet.save()

            # Начисление средств
            destination_wallet.balance += amount
            destination_wallet.save()

            # Создание основной транзакции
            serializer.save()


# Transaction Detail View
class TransactionDetailView(RetrieveDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
