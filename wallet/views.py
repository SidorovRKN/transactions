from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer


# Унифицированная пагинация
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# Wallet List View
class WalletListView(APIView):
    # permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_summary="Retrieve a list of wallets",
        operation_description="Returns a paginated list of wallets with optional filtering by label.",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='Page number',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description='Number of items per page',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'label',
                openapi.IN_QUERY,
                description='Filter by wallet label',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "sort",
                openapi.IN_QUERY,
                description="Sort by balance (asc/desc)",
                type=openapi.TYPE_STRING,
                enum=["asc", "desc"],
            ),
        ],
        responses={200: WalletSerializer(many=True)},
    )
    def get(self, request):
        wallets = Wallet.objects.all()
        label = request.query_params.get('label', None)
        sort = request.query_params.get('sort', "asc")

        if label:
            wallets = wallets.filter(label__icontains=label)

        if sort == "asc":
            wallets = wallets.order_by("balance")
        elif sort == "desc":
            wallets = wallets.order_by("-balance")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(wallets, request, view=self)

        serializer = WalletSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new wallet",
        request_body=WalletSerializer,
        responses={201: WalletSerializer, 400: "Validation Error"},
    )
    def post(self, request):
        serializer = WalletSerializer(data=request.data)
        if serializer.is_valid():
            wallet = serializer.save()
            return Response(WalletSerializer(wallet).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Wallet Detail View
class WalletDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve wallet details",
        responses={200: WalletSerializer, 404: "Not Found"},
    )
    def get(self, request, pk):
        wallet = get_object_or_404(Wallet, pk=pk)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Delete a wallet",
        responses={204: "No Content", 404: "Not Found"},
    )
    def delete(self, request, pk):
        wallet = get_object_or_404(Wallet, pk=pk)
        wallet.delete()
        return Response({'detail': 'Deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


# Transaction List View
class TransactionListView(APIView):
    # permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "wallet",
                openapi.IN_QUERY,
                description="Filter by wallet ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "txid",
                openapi.IN_QUERY,
                description="Filter by txid(partial match)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='Page number',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description='Number of items per page',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "sort",
                openapi.IN_QUERY,
                description="Sort by amount (asc/desc)",
                type=openapi.TYPE_STRING,
                enum=["asc", "desc"],
            ),
        ],
        responses={200: TransactionSerializer(many=True)},
    )
    def get(self, request):
        transactions = Transaction.objects.all()
        wallet_id = request.query_params.get('wallet', None)
        txid = request.query_params.get('txid', None)
        sort = request.query_params.get('sort', "asc")

        if wallet_id:
            transactions = transactions.filter(wallet__id=wallet_id)
        if txid:
            transactions = transactions.filter(txid__icontains=txid)

        if sort == "asc":
            transactions = transactions.order_by("amount")
        elif sort == "desc":
            transactions = transactions.order_by("-amount")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(transactions, request)
        serializer = TransactionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new transaction",
        request_body=TransactionSerializer,
        responses={201: TransactionSerializer, 400: "Validation Error"},
    )
    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                transaction = serializer.save()
            except ValidationError as e:
                return Response(data={"Error": e}, status=400)
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Transaction Detail View
class TransactionDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve transaction details",
        responses={200: TransactionSerializer, 404: "Not Found"},
    )
    def get(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Delete a transaction",
        responses={204: "No Content", 404: "Not Found"},
    )
    def delete(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk)
        transaction.delete()
        return Response({'detail': 'Deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
