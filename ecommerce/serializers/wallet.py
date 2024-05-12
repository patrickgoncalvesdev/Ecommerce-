from rest_framework import serializers
from ecommerce.models.wallet import Wallet
from ecommerce.utils.wallet import truncate


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=19, decimal_places=10, read_only=True)
    class Meta:
        model = Wallet
        fields = ["id", "money", "bonus", "commission", "balance", "is_active"]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["balance"] = truncate(float(data["balance"]), 2)
        data["money"] = truncate(float(data["money"]), 2)
        data["bonus"] = truncate(float(data["bonus"]), 2)
        data["commission"] = truncate(float(data["commission"]), 2)
        return data
    