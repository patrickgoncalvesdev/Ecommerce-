from django.db import models
from ecommerce.models.pule import Pule
from ecommerce.models.money_moviment import MoneyMoviment
from ecommerce.utils import get_locale_formatted_value, string_to_tuple


class Bet(models.Model):
    lotery_key = models.CharField(max_length=255)
    pule = models.ForeignKey(Pule, on_delete=models.PROTECT, related_name="bets")
    user = models.ForeignKey("UserAPI", on_delete=models.PROTECT, related_name="bets")
    bet_value = models.DecimalField(max_digits=19, decimal_places=10)
    guess = models.CharField(max_length=255)
    cashout = models.DecimalField(default=0, max_digits=19, decimal_places=10)
    profit = models.DecimalField(default=0, max_digits=19, decimal_places=10)
    modality_name = models.CharField(max_length=255)
    award_ranges = models.CharField(max_length=255)
    win = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    win_multiplier = models.DecimalField(default=1, max_digits=10, decimal_places=2)
    draw_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def username(self):
        return self.user.username

    @property
    def position(self):
        return self.pule.placing.name

    def to_win(self):
        if not self.is_active:
            raise Exception("A aposta não está ativa.")
        self.win = True
        self.profit = (self.bet_value * self.win_multiplier) - self.bet_value
        self.cashout = self.bet_value * self.win_multiplier
        self.save()
        Pule.objects.select_for_update().get(id=self.pule.id).to_win(
            self.profit, self.cashout
        )
        MoneyMoviment.create_a_win_money_moviment(self, self.pule.user.quotation)

    def get_bet_relatory(self):
        data = string_to_tuple(self.award_ranges)
        output_str = ""
        for i in range(data[0], data[1] + 1):
            output_str += f"{self.modality_name[0]};{i};{self.guess};{get_locale_formatted_value(self.bet_value,2)}\n"
        return output_str

    class Meta:
        verbose_name = "Aposta"
        verbose_name_plural = "Apostas"
