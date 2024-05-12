from rest_framework import serializers
from ecommerce.utils.consts import PuleType
from ecommerce.models.cart import PuleCart, BetCart, Cart


class PlacingCartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    award_range = serializers.CharField(max_length=255)
    is_active = serializers.BooleanField()

class ModalityCartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    is_active = serializers.BooleanField()
    max_input_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    min_input_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    number_separator = serializers.BooleanField()
    max_guess_value = serializers.IntegerField()
    max_bet_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    min_bet_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    big_guess = serializers.BooleanField()

class LotteryDrawCartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    date = serializers.DateTimeField()
    is_active = serializers.BooleanField()

class BetSerializer(serializers.Serializer):
    guess = serializers.CharField(max_length=3)
    bet_value = serializers.DecimalField(max_digits=19, decimal_places=10)

    def to_representation(self, instance: BetCart):
        return {
            "bet_value": instance.bet_value,
            "guess": instance.guess,
        }

class PuleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    guesses = serializers.ListField(child=serializers.CharField(max_length=255))
    type = serializers.ChoiceField(choices=PuleType.choices)
    modality = ModalityCartSerializer()
    placing = PlacingCartSerializer()
    lottery_draw = LotteryDrawCartSerializer()
    bets = BetSerializer(many=True)
    
    def to_representation(self, instance: PuleCart):
        return {
            "id": instance.id,
            "value_total": instance.value_total,
            "guesses": instance.guesses,
            "type": instance.type,
            "modality": instance.modality.model_dump(),
            "placing": instance.placing.model_dump() if instance.placing else None,
            "lottery_draw": instance.lottery_draw.model_dump(),
            "bets": [
                bet.model_dump() for bet in instance.bets
            ]
        }
    

class CartSerializer(serializers.Serializer):
    value_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    pules = PuleSerializer(many=True)
    
    def to_representation(self, instance: Cart):
        return {
            "value_total": instance.value_total,
            "pules": [
                pule.model_dump() for pule in instance.pules
            ]
        }
    