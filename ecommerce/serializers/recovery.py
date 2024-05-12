from rest_framework import serializers
from django.contrib.auth.hashers import make_password


class RecoveryPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    message = serializers.CharField(read_only=True, default="Email enviado com sucesso")
    
    def validate(self, attrs: dict):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "As senhas estão distintas", "confirm_password": "As senhas estão distintas"}
            )
        del attrs["confirm_password"]
        attrs["password"] = make_password(attrs["password"])
        return attrs
    