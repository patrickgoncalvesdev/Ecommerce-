from rest_framework import serializers
from django.core.validators import MinValueValidator
from payment.models import WithDrawRequest

from payment.utils import validate_pix_key


class DepositOutSerializer(serializers.Serializer):
    id = serializers.CharField()
    qr_code = serializers.CharField()
    qr_code_base64 = serializers.CharField()


class DepositRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1.0)


class WithDrawRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1.0)
    pix_key = serializers.CharField()

    def __custom_validation(self):
        pix_key = self.validated_data.get("pix_key")
        validate_pix_key(pix_key)

    def is_valid(self, *, raise_exception=False):
        is_valid = super().is_valid(raise_exception=raise_exception)
        self.__custom_validation()
        return is_valid


class WithDrawOutSerializer(serializers.ModelSerializer):
    detail = serializers.SerializerMethodField("get_detail")

    def get_detail(self, obj) -> str:
        return "Solicitação de saque realizada com sucesso."

    class Meta:
        model = WithDrawRequest
        fields = ["detail", "request_id"]


class WithDrawDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = WithDrawRequest
        fields = ["request_id", "value", "pix_key", "status", "created_at"]
