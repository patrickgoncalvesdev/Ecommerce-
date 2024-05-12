from rest_framework import serializers
from ecommerce.models.bet import Bet


class AwardHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = ["id", "username", "modality_name", "guess", "position", "cashout"]
        