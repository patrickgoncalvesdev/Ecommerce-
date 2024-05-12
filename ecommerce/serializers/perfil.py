from rest_framework import serializers
from ecommerce.models.client import Client
from django.contrib.auth.hashers import make_password


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "cpf", "email", "phone"]
        
class PerfilUpdateSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Client
        fields = ["id", "name", "cpf", "email", "phone", "password", "confirm_password"]
        extra_kwargs = {
            "id": {"read_only": True},
            "cpf": {"read_only": True},
            "email": {"read_only": True},
            "password": {"required": False, "write_only": True},
            "confirm_password": {"required": False}
        }
        
    def validate(self, attrs: dict):
        if attrs.get("password") and not attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Confirm password é requerido"})
        elif attrs.get("confirm_password") and not attrs.get("password"):
            raise serializers.ValidationError({"password": "Password é requerido"})
        if attrs.get("password"):
            if attrs["password"] != attrs["confirm_password"]:
                raise serializers.ValidationError(
                    {"password": "As senhas estão distintas", "confirm_password": "As senhas estão distintas"}
                )
            del attrs["confirm_password"]
            attrs["password"] = make_password(attrs["password"])
        return attrs
    