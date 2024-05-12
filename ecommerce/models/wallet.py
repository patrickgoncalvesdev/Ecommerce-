from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class Wallet(models.Model):
    money = models.DecimalField(max_digits=19, decimal_places=10, default=0.00)
    bonus = models.DecimalField(max_digits=19, decimal_places=10, default=5000.00)
    commission = models.DecimalField(max_digits=19, decimal_places=10, default=0.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Carteira"
        verbose_name_plural = "Carteiras"

    @property
    def balance(self):
        return self.money + self.bonus + self.commission

    def debit_balance(self, value: Decimal):
        self.money -= value
        if self.money < 0:
            self.bonus += self.money
            self.money = 0
        if self.bonus < 0:
            raise ValidationError({"bet_value": "Saldo insuficiente."})
        self.save()

    def bonus_balance(self, value: Decimal):
        self.bonus += value
        self.save()

    def debit_bonus_balance(self, value: Decimal):
        self.bonus -= value
        if self.bonus < 0:
            raise ValidationError({"bet_value": "Saldo insuficiente."})
        self.save()

    def credit_balance(self, value: Decimal):
        self.money += value
        self.save()

    def commission_balance(self, value: Decimal):
        self.commission += value
        self.save()
