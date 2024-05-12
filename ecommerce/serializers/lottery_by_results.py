from rest_framework import serializers
from ecommerce.models import Lottery
from ecommerce.models.lottery_draw import LotteryDraw
from datetime import datetime
import json


class LotteryDrawToResultSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField()
    
    class Meta:
        model = LotteryDraw
        fields = ["id", "name", "date", "results"]
        
    def get_results(self, instance):
        return json.loads(instance.results) if instance.results else []
    
class ResultSerializer(serializers.ModelSerializer):
    draws = serializers.SerializerMethodField()
    
    class Meta:
        model = Lottery
        fields = ["id", "name", "draws"]
        
    def get_draws(self, instance):
        draws = LotteryDraw.get_by_date_desactive(datetime.now().date(), instance)
        return LotteryDrawToResultSerializer(draws, many=True).data
    