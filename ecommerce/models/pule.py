from django.db import models
from ecommerce.utils.consts import PuleType
from ecommerce.utils.mixins import TimestampMixin
from django.contrib.postgres.fields import ArrayField
from decimal import Decimal
from typing import TYPE_CHECKING
from datetime import date
import uuid


if TYPE_CHECKING:
    from ecommerce.serializers.pule_report import PuleReportQueryParams


def generate_hash():
    while True:
        hash = uuid.uuid4()
        if not Pule.objects.filter(hash=hash).exists():
            return hash


class Pule(TimestampMixin, models.Model):
    lotery_key = models.CharField(max_length=255)
    user = models.ForeignKey("UserAPI", on_delete=models.PROTECT, related_name="pules")
    hash = models.UUIDField(default=generate_hash, editable=False, unique=True)
    modality = models.ForeignKey(
        "Modality", on_delete=models.PROTECT, related_name="bets"
    )
    placing = models.ForeignKey(
        "Placing", on_delete=models.PROTECT, related_name="bets", null=True, blank=True
    )
    lottery_draw = models.ForeignKey(
        "LotteryDraw", on_delete=models.PROTECT, related_name="bets"
    )
    value_total = models.DecimalField(max_digits=10, decimal_places=2)
    guesses = ArrayField(models.CharField(max_length=255))
    cashout = models.DecimalField(default=0, max_digits=19, decimal_places=10)
    profit = models.DecimalField(default=0, max_digits=19, decimal_places=10)
    win = models.BooleanField(default=False)
    type = models.CharField(max_length=255, choices=PuleType.choices)
    seller = models.ForeignKey(
        "Affiliate",
        on_delete=models.PROTECT,
        related_name="pules_seller",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Cartela"
        verbose_name_plural = "Cartelas"

    def to_win(self, profit: Decimal, cashout: Decimal):
        self.win = True
        self.profit += profit
        self.cashout += cashout
        self.save()

    @staticmethod
    def get_pules(user, query_params: "PuleReportQueryParams"):
        query_params.is_valid(raise_exception=True)
        query = query_params.validated_data
        if "date" in query:
            query["created_at__date"] = query.pop("date")
        return Pule.objects.filter(user=user, **query).order_by("-created_at")

    @staticmethod
    def get_pules_to_users(user, query: dict):
        return Pule.objects.filter(user=user, **query)

    @staticmethod
    def get_days_pule_user(user) -> list[date]:
        return (
            Pule.objects.filter(user=user)
            .distinct("created_at__date")
            .values_list("created_at__date", flat=True)
        )

    def get_client_user(self):
        from ecommerce.models import Client

        return Client.objects.filter(id=self.user.id).first()

    def get_value_per_bet(self):
        return round(self.value_total / len(self.guesses), 2)

    def __str__(self):
        return str(f"Pule: {self.hash} - {self.created_at}")
