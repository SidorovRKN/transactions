from django.urls import path
from .views import WalletListView, WalletDetailView, TransactionListView, TransactionDetailView

urlpatterns = [
    # Маршруты для Wallet
    path('wallets/', WalletListView.as_view(), name='wallet-list'),  # Список кошельков и создание
    path('wallets/<int:pk>/', WalletDetailView.as_view(), name='wallet-detail'),  # Получение и удаление кошелька

    # Маршруты для Transaction
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),  # Список транзакций и создание
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),  # Получение и удаление транзакции
]
