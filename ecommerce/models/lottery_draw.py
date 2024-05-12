import json
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from ecommerce.serializers.lottery_draw_results import LotteryDrawResultSerializer
from ecommerce.utils.consts import MoneyMovimentType
from ecommerce.models.transaction import Transaction
from ecommerce.models.administration import AdministrativeUser, AdministrativeProfile
from ecommerce.models.affiliate import Affiliate
from ecommerce.models.money_moviment import MoneyMoviment
from ecommerce.utils.wallet import truncate
from ecommerce.models.wallet import Wallet


class LotteryDraw(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    draw_trigger_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    lottery = models.ForeignKey(
        "Lottery", on_delete=models.PROTECT, related_name="draws"
    )
    results = models.TextField(blank=True, null=True)

    def add_profits(self):
        temp = {}
        affiliates_to_pay = Affiliate.objects.filter(
            pules_seller__lottery_draw=self
        ).distinct()
        gerentes_to_pay = AdministrativeUser.objects.filter(
            affiliates__in=affiliates_to_pay, profile=AdministrativeProfile.MANAGER
        ).distinct()
        supervisors_to_pay = AdministrativeUser.objects.filter(
            children__in=gerentes_to_pay, profile=AdministrativeProfile.SUPERVISOR
        ).distinct()
        master_to_pay = AdministrativeUser.objects.filter(
            profile=AdministrativeProfile.ADMIN
        ).first()
        for gerente in gerentes_to_pay:
            wallet = Wallet.objects.select_for_update().get(administrative_user=gerente)
            all_sales = MoneyMoviment.objects.filter(
                bet__pule__seller__user_above=gerente, type=MoneyMovimentType.DEBIT
            )
            all_comissions = MoneyMoviment.objects.filter(
                bet__pule__seller__user_above=gerente, type=MoneyMovimentType.COMMISSION
            )
            all_awards = MoneyMoviment.objects.filter(
                bet__pule__seller__user_above=gerente, type=MoneyMovimentType.CREDIT
            )
            total_sales = all_sales.aggregate(total=Sum("value", default=0))["total"]
            total_comissions = all_comissions.aggregate(total=Sum("value", default=0))[
                "total"
            ]
            total_awards = all_awards.aggregate(total=Sum("value", default=0))["total"]
            remains = total_sales - total_comissions - total_awards
            if remains > 0:
                to_manager = truncate(remains * gerente.percent / 100)
                if temp.get(gerente.parent):
                    temp[gerente.parent] += remains - to_manager
                else:
                    temp[gerente.parent] = remains - to_manager
                Transaction.new_commission_transaction(to_manager, wallet, self)
        for supervisor in supervisors_to_pay:
            wallet = Wallet.objects.select_for_update().get(
                administrative_user=supervisor
            )
            remains = temp[supervisor]
            if remains > 0:
                to_supervisor = truncate(remains * supervisor.percent / 100)
                if temp.get(supervisor.parent):
                    temp[supervisor.parent] += remains - to_supervisor
                else:
                    temp[supervisor.parent] = remains - to_supervisor
                Transaction.new_commission_transaction(to_supervisor, wallet, self)
        to_master = temp.get(master_to_pay, 0)
        all_sales_without_seller = MoneyMoviment.objects.filter(
            bet__pule__seller=None, type=MoneyMovimentType.DEBIT
        )
        all_awards_without_seller = MoneyMoviment.objects.filter(
            bet__pule__seller=None, type=MoneyMovimentType.CREDIT
        )
        total_sales_without_seller = all_sales_without_seller.aggregate(
            total=Sum("value", default=0)
        )["total"]
        total_awards_without_seller = all_awards_without_seller.aggregate(
            total=Sum("value", default=0)
        )["total"]
        remains = total_sales_without_seller - total_awards_without_seller + to_master
        if remains > 0:
            wallet = Wallet.objects.select_for_update().get(
                administrative_user=master_to_pay
            )
            Transaction.new_commission_transaction(remains, wallet, self)

    def end_draw(self, results: str):
        self.results = results
        self.is_active = False
        self.save()

    def check_to_purchase(self):
        now_sub_1_hour = timezone.now() + timezone.timedelta(hours=1)
        if not self.is_active or now_sub_1_hour > self.date:
            raise serializers.ValidationError(
                {
                    "lottery_draw": f"Este sorteio {self.id} - {self.name} não está mais ativo."
                }
            )
        elif not self.lottery.is_active:
            raise serializers.ValidationError(
                {
                    "lottery": f"Esta loteria {self.lottery.id} - {self.lottery.name} não está mais ativa."
                }
            )

    @staticmethod
    def get_days(lottery):
        current_timezone = timezone.get_current_timezone()
        now = timezone.now().astimezone(current_timezone)
        now_sum_1_hour = now + timezone.timedelta(hours=1)
        return (
            LotteryDraw.objects.filter(
                lottery=lottery, date__gt=now_sum_1_hour, is_active=True
            )
            .values_list("date__date", flat=True)
            .distinct()
            .order_by("date__date")
        )

    @staticmethod
    def get_by_date(date, lottery):
        return LotteryDraw.objects.filter(
            lottery=lottery, date__date=date, is_active=True
        ).order_by("date")

    @staticmethod
    def get_by_date_desactive(date, lottery):
        return LotteryDraw.objects.filter(
            lottery=lottery, date__date=date, is_active=False
        ).order_by("date")

    @staticmethod
    def get_by_datetime_gt(date, lottery, now):
        return LotteryDraw.objects.filter(
            lottery=lottery, date__date=date, date__gt=now, is_active=True
        ).order_by("date")

    def get_typed_results(self):
        try:
            data = json.loads(self.results)
            return [LotteryDrawResultSerializer(**result) for result in data]
        except Exception as e:
            print(e)
            return []
    
    def get_bets_relatory(self):
        out_text = ""  # C;5;120;0,05
        pules = self.bets.all()
        for pule in pules:
            for bet in pule.bets.all():
                out_text += bet.get_bet_relatory()
        return out_text

    def __str__(self):
        return f"{self.name} - {self.lottery.name} - {self.date}"

    class Meta:
        verbose_name = "Sorteio da Loteria"
        verbose_name_plural = "Sorteios das Loterias"
