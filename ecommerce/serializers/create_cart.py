from rest_framework import serializers
from ecommerce.models import Bet
from ecommerce.utils.consts import PuleType
from decimal import Decimal
from django.core.cache import cache
from ecommerce.models.cart import PuleCart, BetCart, ModalityCart, PlacingCart, LotteryDrawCart, LotteryCart
from ecommerce.models.modality import Modality
from ecommerce.models.placing import Placing
from ecommerce.models.lottery_draw import LotteryDraw
from ecommerce.utils.game import get_permutations
from ecommerce.utils.wallet import truncate


class CreateCartSerializer(serializers.ModelSerializer):
    guesses = serializers.ListField(child=serializers.CharField(max_length=255))
    type = serializers.ChoiceField(choices=PuleType.choices)
    modality = serializers.PrimaryKeyRelatedField(queryset=Modality.objects.all())
    placing = serializers.PrimaryKeyRelatedField(queryset=Placing.objects.all(), required=False)
    lottery_draw = serializers.PrimaryKeyRelatedField(queryset=LotteryDraw.objects.all())
    
    def validate_bet_value(self, value: Decimal):
        if value <= 0:
            raise serializers.ValidationError("O valor da aposta deve ser maior que zero.")
        return value
    
    class Meta:
        model = Bet
        fields = ["modality", "placing", "lottery_draw", "guesses", "bet_value", "type"]
        
    def validate(self, attrs):
        attrs["lottery_draw"].check_to_purchase()
        lottery = attrs["lottery_draw"].lottery
        if not attrs["modality"] in lottery.modalities.filter(is_active=True):
            raise serializers.ValidationError({"modality": "A modalidade não pertence a loteria selecionada."})
        placements = attrs["modality"].placements.filter(is_active=True)
        if placements:
            if not attrs.get("placing"):
                raise serializers.ValidationError({"placing": "A modalidade selecionada requer uma colocação."})
            if not attrs["placing"] in placements:
                raise serializers.ValidationError({"placing": "A colocação não pertence a modalidade selecionada."})
        attrs["modality"].validate_guesses(attrs["guesses"])
        attrs["modality"].validate_bet_value(attrs["bet_value"])
        return super().validate(attrs)
    
    def create_pule_cart(self) -> PuleCart:
        modality_model: Modality = self.validated_data["modality"]
        modality_name = modality_model.name
        guesses = self.validated_data["guesses"]
        pule_value = truncate(self.validated_data["bet_value"] if self.validated_data["type"] == PuleType.ALL else self.validated_data["bet_value"] * len(self.validated_data["guesses"]), 2)
        if modality_model.ref:
            modality_name = modality_model.ref.name
            guesses = []
            for guess in self.validated_data["guesses"]:
                guesses += get_permutations(guess, modality_model.ref.name)
        bet_value = truncate(pule_value / len(guesses))
        modality = ModalityCart(**self.validated_data["modality"].__dict__)
        placing = None
        if self.validated_data.get("placing"):
            placing = PlacingCart(**self.validated_data["placing"].__dict__)
        lottery = LotteryCart(**self.validated_data["lottery_draw"].lottery.__dict__)
        lottery_draw = LotteryDrawCart(**self.validated_data["lottery_draw"].__dict__, lottery=lottery)
        bets = [BetCart(guess=guess, bet_value=bet_value, modality_name=modality_name) for guess in guesses]
        if pule_value > modality_model.max_bet_value:
            raise serializers.ValidationError(
                {
                    "bet_value": f"O valor da aposta é maior que o valor máximo permitido para a modalidade {modality_model.name}."
                }
            )
        if not cache.get("pule_id"):
            cache.set("pule_id", 0)
        id = cache.incr("pule_id")
        return PuleCart(id=id, value_total=pule_value, guesses=self.validated_data["guesses"], type=self.validated_data["type"], modality=modality, placing=placing, lottery_draw=lottery_draw, bets=bets)
    