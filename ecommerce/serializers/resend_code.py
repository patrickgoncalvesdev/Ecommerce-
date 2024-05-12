from rest_framework import serializers
from ecommerce.models.user import UserAPI


class ResendCodeInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        user = UserAPI.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("Usuário não encontrado")
        self.instance = user
        return value