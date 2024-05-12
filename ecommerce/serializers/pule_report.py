from rest_framework import serializers
from ecommerce.models.pule import Pule
from ecommerce.models.bet import Bet
from ecommerce.models.modality import Modality
from ecommerce.models.placing import Placing
from ecommerce.models.lottery_draw import LotteryDraw


class ModalityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modality
        fields = ["id", "name"]
        
class PlacingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placing
        fields = ["id", "name"]
        
class LotteryDrawReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LotteryDraw
        fields = ["id", "name", "date"]

class BetReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = ["id", "bet_value", "guess", "cashout", "profit", "win"]

class PuleReportSerializer(serializers.ModelSerializer):
    bets = BetReportSerializer(many=True)
    modality = ModalityReportSerializer()
    placing = PlacingReportSerializer()
    lottery_draw = LotteryDrawReportSerializer()
    
    class Meta:
        model = Pule
        fields = ["id", "hash", "value_total", "guesses", "cashout", "profit", "win", "type", "bets", "modality", "placing", "lottery_draw", "created_at", "updated_at"]
        
class PuleReportQueryParams(serializers.Serializer):
    hash = serializers.UUIDField(required=False)
    date = serializers.DateField(required=False)
    