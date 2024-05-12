from rest_framework import serializers
from ecommerce.models.pule import Pule
from ecommerce.models.bet import Bet


class PuleUserQueryParams(serializers.Serializer):
    win = serializers.BooleanField(required=False)
    
class BetPuleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = ["id", "bet_value", "guess", "win", "cashout", "profit"]
    
class PuleUserSerializer(serializers.ModelSerializer):
    bets = BetPuleUserSerializer(many=True)
    modality_name = serializers.CharField(source="modality.name")
    placing_name = serializers.CharField(source="placing.name")
    lottery_draw_name = serializers.CharField(source="lottery_draw.name")
    
    class Meta:
        model = Pule
        fields = ["id", "hash", "value_total", "guesses", "cashout", "profit", "win", "type", "modality_name", "placing_name", "lottery_draw_name", "created_at", "updated_at", "bets"]
