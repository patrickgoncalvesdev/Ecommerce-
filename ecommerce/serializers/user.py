from rest_framework import serializers
from ecommerce.models.user import UserAPI
from ecommerce.serializers.wallet import WalletSerializer



class UserSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer()
    
    class Meta:
        model = UserAPI
        fields = ["id", "name", "last_login", "username", "cpf", "email", "phone", "birth_date", "wallet"]
        