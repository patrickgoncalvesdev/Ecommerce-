from rest_framework import serializers
from ecommerce.models import Lottery
from ecommerce.serializers.modality import ModalitySerializer
from ecommerce.models.lottery_draw import LotteryDraw
from django.utils import timezone


class LotteryDrawToLotterySerializer(serializers.ModelSerializer):
    class Meta:
        model = LotteryDraw
        exclude = ['lottery', "results", "is_active"]
        
class DaysSerializer(serializers.Serializer):
    date = serializers.DateField()
    draws = LotteryDrawToLotterySerializer(many=True)
    
    def to_representation(self, instance):
        payload =  super().to_representation(instance)
        draws = payload.pop('draws')
        payload['draws'] = draws
        return payload

class LotterySerializer(serializers.ModelSerializer):
    modalities = ModalitySerializer(many=True)
    days = serializers.SerializerMethodField()
    
    class Meta:
        model = Lottery
        fields = ["id", "name", "modalities", "days"]
    
    def get_days(self, instance):
        days = LotteryDraw.get_days(instance)
        response = []
        current_timezone = timezone.get_current_timezone()
        now = timezone.now().astimezone(current_timezone)
        now_sum_1_hour = now + timezone.timedelta(hours=1)
        for day in days:
            draws = LotteryDraw.get_by_datetime_gt(day, instance, now_sum_1_hour)
            response.append({
                "date": day,
                "draws": LotteryDrawToLotterySerializer(draws, many=True).data
            })
        return DaysSerializer(response, many=True).data
        
    def to_representation(self, instance):
        payload =  super().to_representation(instance)
        modalities = payload.pop('modalities')
        payload['modalities'] = modalities
        return payload