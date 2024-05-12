from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from ecommerce.models.transaction import Transaction
from ecommerce.models.user import UserAPI
from ecommerce.utils.swagger import ErrorDetail
from drf_yasg.utils import swagger_auto_schema
from payment.base import PaymentBaseClass
from payment.consts import PaymentTypeChoices, PaymentStatus
from payment.models import PaymentConfigTable, WithDrawRequest
from payment.serializers import (
    DepositOutSerializer,
    DepositRequestSerializer,
    WithDrawDetailSerializer,
    WithDrawOutSerializer,
    WithDrawRequestSerializer,
)
from rest_framework.exceptions import ValidationError


class WebhookView(APIView):
    # mercado pago
    def post(self, request: Request):
        if request.headers.get("Referer") == "https://mercadopago.com.ar":
            data = json.loads(request.body)
            if data["action"] == "payment.updated":
                try:
                    payment_id = data["data"]["id"]
                    PaymentBaseClass().validate_payment(payment_id)
                except Exception as e:
                    print(f"Error validating payment: {e}, type: {type(e)}")
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=DepositRequestSerializer,
        responses={200: DepositOutSerializer, 401: ErrorDetail},
    )
    def post(self, request: Request):
        serializer = DepositRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserAPI.objects.get(username=request.user.username)
        config = PaymentConfigTable.get_config()
        if not config.deposit_value_is_valid(serializer.validated_data["amount"]):
            raise ValidationError(
                {
                    "detail": f"Valor de depósito inválido, escolha um valor entre {config.min_deposit_value} e {config.max_deposit_value}"
                },
            )
        result = PaymentBaseClass().pix_payment_request(
            user=user,
            value=serializer.validated_data["amount"],
            type=PaymentTypeChoices.PIX,
        )
        return Response(
            DepositOutSerializer(result.model_dump()).data,
            status=status.HTTP_201_CREATED,
        )


class WithDrawView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=WithDrawRequestSerializer,
        responses={200: WithDrawOutSerializer, 401: ErrorDetail},
    )
    def post(self, request: Request):
        serializer = WithDrawRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserAPI.objects.get(username=request.user.username)
        config = PaymentConfigTable.get_config()
        if serializer.validated_data["amount"] > user.wallet.money:
            raise ValidationError(
                {
                    "detail": "Saldo insuficiente para realizar o saque.",
                },
            )
        if not config.verify_if_user_can_create_a_withdraw_request(
            withdraw_value=serializer.validated_data["amount"], user=user
        ):
            raise ValidationError(
                {
                    "detail": "Limite de saques diários atingido, tente novamente amanhã."
                },
            )
        if not config.withdraw_value_is_valid(serializer.validated_data["amount"]):
            raise ValidationError(
                {
                    "detail": f"Valor de saque inválido, escolha um valor entre {config.min_withdraw_value} e {config.max_withdraw_value}"
                },
            )

        withdraw_request = WithDrawRequest.objects.create(
            user=user,
            value=serializer.validated_data["amount"],
            pix_key=serializer.validated_data["pix_key"],
        )
        withdraw_transaction = Transaction.new_withdraw_transaction(
            wallet=user.wallet, value=serializer.validated_data["amount"]
        )
        withdraw_request.money_transaction = withdraw_transaction
        withdraw_request.save()
        return Response(
            data=WithDrawOutSerializer(withdraw_request).data,
        )


class PendingWithDrawView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: WithDrawDetailSerializer(many=True)},
    )
    def get(self, request):
        pending_withdraws = WithDrawRequest.objects.filter(
            status=PaymentStatus.PENDING,
            user=UserAPI.objects.get(username=request.user.username),
        )
        serialized_data = WithDrawDetailSerializer(pending_withdraws, many=True).data
        return Response(serialized_data)
