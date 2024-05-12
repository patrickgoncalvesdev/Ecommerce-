from decimal import Decimal
from django.db import models
from ecommerce.utils.consts import MoneyMovimentType, MoneyMovimentStatus
from ecommerce.models.wallet import Wallet
from typing import TYPE_CHECKING
from datetime import date
from django.db.models import Sum

if TYPE_CHECKING:
    from ecommerce.models import Bet
    from ecommerce.serializers.statement_report import StatementReportQueryParams
    from ecommerce.models.quotation import Quotation


class MoneyMoviment(models.Model):
    wallet = models.ForeignKey(
        "Wallet", on_delete=models.PROTECT, related_name="money_moviments"
    )
    quotation = models.ForeignKey(
        "Quotation",
        on_delete=models.PROTECT,
        related_name="money_moviments",
        blank=True,
        null=True,
    )
    bet = models.ForeignKey(
        "Bet", on_delete=models.PROTECT, related_name="money_moviments"
    )
    value = models.DecimalField(max_digits=19, decimal_places=10)
    type = models.CharField(max_length=255, choices=MoneyMovimentType.choices)
    status = models.CharField(max_length=255, choices=MoneyMovimentStatus.choices)
    balance_before = models.DecimalField(max_digits=19, decimal_places=10)
    balance_after = models.DecimalField(max_digits=19, decimal_places=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_a_win_money_moviment(
        cls: "MoneyMoviment", bet: "Bet", quotation: "Quotation" = None
    ):
        wallet = Wallet.objects.select_for_update().get(user=bet.user)
        balance_before = wallet.balance
        value = bet.cashout
        wallet.credit_balance(value)
        if not quotation:
            quotation = bet.user.quotation
        return cls.objects.create(
            wallet=wallet,
            bet=bet,
            value=value,
            quotation=quotation,
            type=MoneyMovimentType.CREDIT,
            status=MoneyMovimentStatus.APPROVED,
            balance_before=balance_before,
            balance_after=wallet.balance,
        )

    @classmethod
    def new_commission_transaction(
        cls, value: Decimal, wallet: "Wallet", bet: "Bet", quotation: "Quotation" = None
    ):
        balance_before = wallet.balance
        wallet.commission_balance(value)
        return cls.objects.create(
            wallet=wallet,
            value=value,
            bet=bet,
            quotation=quotation,
            type=MoneyMovimentType.COMMISSION,
            status=MoneyMovimentStatus.APPROVED,
            balance_before=balance_before,
            balance_after=wallet.balance,
        )

    @staticmethod
    def get_days_moviment_user(user) -> list[date]:
        return (
            MoneyMoviment.objects.filter(wallet__user=user)
            .distinct("created_at__date")
            .values_list("created_at__date", flat=True)
        )

    @staticmethod
    def get_grouped_moviment_user_to_report(
        user, query_params: "StatementReportQueryParams"
    ) -> dict:
        query_params.is_valid(raise_exception=True)
        query = query_params.validated_data
        statements = MoneyMoviment.objects.filter(
            wallet__user=user, created_at__date=query["date"]
        ).order_by("created_at")
        response = statements.aggregate(
            credit=Sum(
                "value", filter=models.Q(type=MoneyMovimentType.CREDIT), default=0
            ),
            debit=Sum(
                "value", filter=models.Q(type=MoneyMovimentType.DEBIT), default=0
            ),
        )
        response["balance_before"] = (
            statements.first().balance_before if statements else 0
        )
        response["balance_after"] = statements.last().balance_after if statements else 0
        return response

    class Meta:
        verbose_name = "Movimento do dinheiro da aposta"
        verbose_name_plural = "Movimentos do dinheiro das apostas"

    def __str__(self) -> str:
        return f"{self.wallet.user.username} - {self.bet.modality_name} - {self.value}"
