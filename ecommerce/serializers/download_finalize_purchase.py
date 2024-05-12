from rest_framework import serializers
from ecommerce.models.pule import Pule
from ecommerce.models.affiliate import Affiliate
from ecommerce.models.modality import Modality
from ecommerce.models.lottery_draw import LotteryDraw
from ecommerce.models.placing import Placing
from ecommerce.models.lottery import Lottery


class DownloadSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliate
        fields = ["name"]
        
class DownloadPlacingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placing
        fields = ["name"]

class DownloadPurchaseModalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Modality
        exclude = ["placements", "ref"]

class DownloadLotterySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    
    class Meta:
        model = Lottery
        fields = ["name"]
        
class DownloadPurchaseLotteryDrawSerializer(serializers.ModelSerializer):
    lottery = DownloadLotterySerializer()
    
    class Meta:
        model = LotteryDraw
        exclude = ["draw_trigger_date", "results"]

class DownloadPurchasePuleSerializer(serializers.ModelSerializer):
    modality = DownloadPurchaseModalitySerializer()
    lottery_draw = DownloadPurchaseLotteryDrawSerializer()
    id = serializers.IntegerField()
    hash = serializers.CharField()
    seller = DownloadSellerSerializer(default=None, allow_null=True)
    created_at = serializers.DateTimeField()
    placing = DownloadPlacingSerializer()
    
    class Meta:
        model = Pule
        exclude = ["user", "lotery_key", "cashout", "profit", "win"]
        depth = 2

class DownloadPurchaseSerializer(serializers.Serializer):
    pules = DownloadPurchasePuleSerializer(many=True)
    