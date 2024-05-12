from django.db import models
from ecommerce.models.affiliate_quotation import AffiliateQuotation
from ecommerce.models.user import UserAPI
from ecommerce.models.administration import AdministrativeUser
from django.utils.crypto import get_random_string
from ecommerce.models.money_moviment import MoneyMoviment
from ecommerce.utils.consts import (
    MoneyMovimentType,
    MoneyMovimentStatus,
    CommissionEnum,
)
from django.db.models import Sum
from decimal import Decimal


def generate_code_affiliate():
    code = get_random_string(length=4)
    if Affiliate.objects.filter(code=code).exists():
        return generate_code_affiliate()
    return code


class Affiliate(UserAPI):
    user_above = models.ForeignKey(AdministrativeUser, on_delete=models.CASCADE, related_name="affiliates")
    commission = models.CharField(
        max_length=10, choices=CommissionEnum.choices, default=CommissionEnum.GROSS
    )

    class Meta:
        verbose_name = "Afiliado"
        verbose_name_plural = "Afiliados"

    @property
    def user_above_name(self):
        return self.user_above.first_name

    class Meta:
        verbose_name = "Afiliado"
        verbose_name_plural = "Afiliados"
        
    def sells(self, filter: dict = {}):
        """Exibir na dash"""
        statements = MoneyMoviment.objects.filter(
            bet__pule__seller=self,
            type=MoneyMovimentType.DEBIT,
            status=MoneyMovimentStatus.APPROVED,
            **filter
        )
        aggregate = statements.aggregate(sells=Sum("value", default=0))
        return aggregate["sells"]
    
    def commissions_with_my(self, filter: dict = {}):
        """Exibir na dash"""
        statements = MoneyMoviment.objects.filter(
            wallet__user=self,
            type=MoneyMovimentType.COMMISSION,
            status=MoneyMovimentStatus.APPROVED,
            **filter
        )
        aggregate = statements.aggregate(commissions_with_my=Sum("value", default=0))
        return aggregate["commissions_with_my"]
    
    def total_with_my(self, filter: dict = {}):
        """Exibir na dash"""
        return self.sells(filter) - self.commissions_with_my(filter) - self.awards(filter)

    def sales(self, filter: dict = {}):
        statements = MoneyMoviment.objects.filter(
            bet__pule__seller=self,
            type=MoneyMovimentType.DEBIT,
            status=MoneyMovimentStatus.APPROVED,
            **filter
        )
        aggregate = statements.aggregate(sales=Sum("value", default=0))
        return aggregate["sales"]

    def commissions(self, filter: dict = {}):
        statements = MoneyMoviment.objects.filter(
            wallet__user=self,
            type=MoneyMovimentType.COMMISSION,
            status=MoneyMovimentStatus.APPROVED,
            **filter
        )
        aggregate = statements.aggregate(commissions=Sum("value", default=0))
        return aggregate["commissions"]

    def awards(self, filter: dict = {}):
        statements = MoneyMoviment.objects.filter(
            bet__pule__seller=self,
            type=MoneyMovimentType.CREDIT,
            status=MoneyMovimentStatus.APPROVED,
            **filter
        )
        aggregate = statements.aggregate(awards=Sum("value", default=0))
        return aggregate["awards"]

    def total(self, filter: dict = {}) -> Decimal:
        sales = self.sales(filter)
        commissions = self.commissions(filter)
        awards = self.awards(filter)
        return sales - commissions - awards

    def get_all_affiliate_quotations(self):
        return AffiliateQuotation.objects.filter(affiliate=self)
