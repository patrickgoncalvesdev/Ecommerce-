from django.db import models
from ecommerce.models.config import Config


class FirstDeposit(models.Model):
    value = models.DecimalField(max_digits=10, decimal_places=2, default=300)
    percent = models.DecimalField(max_digits=10, decimal_places=2, default=25)

    class Meta:
        verbose_name = "Primeiro Depósito"
        verbose_name_plural = "Primeiros Depósitos"
        
    def __str__(self) -> str:
        return f"Primeiro Depósito"
        
    def desactive_others(self):
        config = Config.objects.last()
        if config:
            config.deposit = self
            config.save()
        FirstDeposit.objects.exclude(id=self.id).delete()
        