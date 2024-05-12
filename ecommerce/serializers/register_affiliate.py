from rest_framework import serializers
from ecommerce.models.affiliate import Affiliate
from ecommerce.models.administration import AdministrativeUser, AdministrativeProfile
from ecommerce.models.config import Config


class RegisterAffiliateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    gerente = serializers.PrimaryKeyRelatedField(write_only=True, queryset=AdministrativeUser.objects.filter(is_active=True, profile=AdministrativeProfile.MANAGER), source="user_above")

    class Meta:
        model = Affiliate
        fields = [
            "username",
            "name",
            "email",
            "cpf",
            "password",
            "confirm_password",
            "phone",
            "gerente"
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs: dict):
        self._validate_passwords(attrs)
        self._validate_cpf(attrs["cpf"])
        del attrs["confirm_password"]
        return attrs
    
    def _validate_passwords(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "password": "As senhas estão distintas",
                    "confirm_password": "As senhas estão distintas",
                }
            )

    def _validate_cpf(self, cpf):
        if len(cpf) != 11:
            raise serializers.ValidationError("O CPF deve conter 11 dígitos")

        if len(set(cpf)) == 1:
            raise serializers.ValidationError("CPF inválido")

        if not self._validate_cpf_format(cpf):
            raise serializers.ValidationError("CPF inválido")

    def _validate_cpf_format(self, cpf):
        cpf_list = [int(digit) for digit in cpf]

        if cpf_list == cpf_list[::-1]:
            return False

        weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        sum_ = sum(cpf_list[i] * weights[i] for i in range(9))
        remainder = sum_ % 11
        if remainder < 2:
            if cpf_list[9] != 0:
                return False
        else:
            if cpf_list[9] != 11 - remainder:
                return False

        weights = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        sum_ = sum(cpf_list[i] * weights[i] for i in range(10))
        remainder = sum_ % 11
        if remainder < 2:
            if cpf_list[10] != 0:
                return False
        else:
            if cpf_list[10] != 11 - remainder:
                return False

        return True


class RegisterAffiliateOutPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliate
        fields = ["username", "email", "cpf"]
        