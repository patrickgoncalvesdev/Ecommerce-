from decimal import Decimal
from django.db import models
from ecommerce.utils.consts import MoneyMovimentType, MoneyMovimentStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ecommerce.models import Wallet
    from ecommerce.models import LotteryDraw


class Transaction(models.Model):
    wallet: "Wallet" = models.ForeignKey(
        "Wallet", on_delete=models.PROTECT, related_name="transações"
    )
    draw = models.ForeignKey("LotteryDraw", on_delete=models.PROTECT, related_name="transações", blank=True, null=True)
    value = models.DecimalField(max_digits=19, decimal_places=10)
    type = models.CharField(max_length=255, choices=MoneyMovimentType.choices)
    status = models.CharField(max_length=255, choices=MoneyMovimentStatus.choices)
    balance_before = models.DecimalField(max_digits=19, decimal_places=10)
    balance_after = models.DecimalField(max_digits=19, decimal_places=10)
    created_by = models.ForeignKey(
        "ecommerce.AdministrativeUser", on_delete=models.PROTECT, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transação do dinheiro"
        verbose_name_plural = "Transações dos dinheiros"

    @classmethod
    def new_deposit_transaction(cls, value: Decimal, wallet: "Wallet"):
        balance_before = wallet.balance
        wallet.credit_balance(value)
        return cls.objects.create(
            wallet=wallet,
            value=value,
            type=MoneyMovimentType.DEPOSIT,
            status=MoneyMovimentStatus.APPROVED,
            balance_before=balance_before,
            balance_after=wallet.balance,
        )

    @classmethod
    def new_bonus_transaction(cls, value: Decimal, wallet: "Wallet", created_by=None):
        balance_before = wallet.balance
        wallet.bonus_balance(value)
        return cls.objects.create(
            wallet=wallet,
            value=value,
            type=MoneyMovimentType.BONUS,
            status=MoneyMovimentStatus.APPROVED,
            balance_before=balance_before,
            balance_after=wallet.balance,
            created_by=created_by,
        )

    @classmethod
    def new_debit_bonus_transaction(
        cls, value: Decimal, wallet: "Wallet", created_by=None
    ):
        balance_before = wallet.balance
        wallet.debit_bonus_balance(value)
        return cls.objects.create(
            wallet=wallet,
            value=value,
            type=MoneyMovimentType.BONUS_DEBIT,
            status=MoneyMovimentStatus.APPROVED,
            balance_before=balance_before,
            balance_after=wallet.balance,
            created_by=created_by,
        )

    @classmethod
    def new_commission_transaction(
        cls, value: Decimal, wallet: "Wallet", draw: "LotteryDraw"
    ):
        balance_before = wallet.balance
        wallet.commission_balance(value)
        return cls.objects.create(
            wallet=wallet,
            value=value,
            draw=draw,
            type=MoneyMovimentType.COMMISSION,
            status=MoneyMovimentStatus.APPROVED,
            balance_before=balance_before,
            balance_after=wallet.balance,
        )

    @classmethod
    def new_withdraw_transaction(cls, value: Decimal, wallet: "Wallet"):
        balance_before = wallet.balance
        wallet.debit_balance(value)
        return cls.objects.create(
            wallet=wallet,
            value=value,
            type=MoneyMovimentType.WITHDRAW,
            status=MoneyMovimentStatus.APPROVED,
            balance_before=balance_before,
            balance_after=wallet.balance,
        )

    def refund_transaction(self):
        if self.type == MoneyMovimentType.WITHDRAW:
            self.wallet.credit_balance(self.value)
        self.status = MoneyMovimentStatus.CANCELED
        self.save()

    def __str__(self) -> str:
        return f"{self.wallet.id} - {self.type} - {self.value}"
