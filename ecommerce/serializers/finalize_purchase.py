from rest_framework import serializers
from ecommerce.models.pule import Pule
from ecommerce.models.bet import Bet
from ecommerce.models.money_moviment import MoneyMoviment
from ecommerce.utils.consts import MoneyMovimentType, MoneyMovimentStatus
from ecommerce.models.modality import Modality
from ecommerce.models.quotation_modality import QuotationModality
from ecommerce.models.lottery_draw import LotteryDraw
from ecommerce.models.lottery import Lottery
from decimal import Decimal
from ecommerce.models.wallet import Wallet
from ecommerce.utils.wallet import truncate
from ecommerce.models.affiliate import Affiliate


class CreatePuleBetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = ["guess", "bet_value"]


class CreatePuleSerializer(serializers.ModelSerializer):
    def validate_bet_value(self, value: Decimal):
        if value <= 0:
            raise serializers.ValidationError(
                "O valor da aposta deve ser maior que zero."
            )
        return value

    class Meta:
        model = Pule
        fields = [
            "modality",
            "placing",
            "lottery_draw",
            "value_total",
            "guesses",
            "type",
        ]

    def validate(self, attrs):
        attrs["lottery_draw"].check_to_purchase()
        lottery = attrs["lottery_draw"].lottery
        if not attrs["modality"] in lottery.modalities.filter(is_active=True):
            raise serializers.ValidationError(
                {"modality": "A modalidade não pertence a loteria selecionada."}
            )
        placements = attrs["modality"].placements.filter(is_active=True)
        if placements:
            if not attrs.get("placing"):
                raise serializers.ValidationError(
                    {"placing": "A modalidade selecionada requer uma colocação."}
                )
            if not attrs["placing"] in placements:
                raise serializers.ValidationError(
                    {"placing": "A colocação não pertence a modalidade selecionada."}
                )
        attrs["modality"].validate_guesses(attrs["guesses"])
        attrs["modality"].validate_bet_value(attrs["value_total"])
        attrs["lotery_key"] = lottery.lotery_key
        return super().validate(attrs)

    def create(self, validated_data: dict):
        wallet = self.context["wallet"]
        validated_data["user"] = wallet.user
        try:
            # TODO Melhorar a logica futuramente
            validated_data["seller"] = validated_data["user"].client.associated_affiliate
        except AttributeError:
            pass
        pule = super().create(validated_data)
        placing_modality = QuotationModality.objects.filter(
            modality=validated_data["modality"], quotation=validated_data["user"].quotation
        ).first()
        if not placing_modality or not validated_data["user"].quotation:
            raise serializers.ValidationError(
                {"quotation": "Cotação indisponivel."}
            )
        quantity = validated_data["placing"].award_range
        numero1, numero2 = map(int, quantity.split(','))
        for bet in self.context["bets"]:
            bet = Bet.objects.create(
                draw_date=validated_data["lottery_draw"].date,
                lotery_key=validated_data["lotery_key"],
                win_multiplier=truncate(placing_modality.multiplier / (numero2 - numero1), 2),
                user=wallet.user,
                pule=pule,
                award_ranges=(
                    validated_data["placing"].award_range
                    if validated_data.get("placing")
                    else ""
                ),
                **bet.model_dump(),
            )
            balance_before = wallet.balance
            wallet.debit_balance(bet.bet_value)
            MoneyMoviment.objects.create(
                wallet=wallet,
                quotation=validated_data["user"].quotation,
                bet=bet,
                value=bet.bet_value,
                type=MoneyMovimentType.DEBIT,
                status=MoneyMovimentStatus.APPROVED,
                balance_before=balance_before,
                balance_after=wallet.balance,
            )
        return pule


class PurchaseAffiliateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliate
        fields = ["name"]

class PurchaseModalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Modality
        exclude = ["placements", "ref"]
        
class PurchaseLotterySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lottery
        fields = ["name"]
        
class PurchaseLotteryDrawSerializer(serializers.ModelSerializer):
    lottery = PurchaseLotterySerializer()
    class Meta:
        model = LotteryDraw
        exclude = ["draw_trigger_date", "results"]

class PurchasePuleSerializer(serializers.ModelSerializer):
    modality = PurchaseModalitySerializer()
    lottery_draw = PurchaseLotteryDrawSerializer()
    seller = PurchaseAffiliateSerializer()
    
    class Meta:
        model = Pule
        exclude = ["user", "lotery_key", "cashout", "profit", "win"]
        depth = 2

class PurchaseWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["balance", "money", "bonus"]
        
class FinalizePurchaseSerializer(serializers.Serializer):
    pules = PurchasePuleSerializer(many=True)
    wallet = PurchaseWalletSerializer()
    cart = serializers.JSONField()
    pdf_id = serializers.CharField()
    