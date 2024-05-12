from django.db import models
from ecommerce.models.config import Config


class AffiliateConfig(models.Model):
    percent = models.DecimalField(max_digits=10, decimal_places=2, default=25)
    quotation = models.ForeignKey("Quotation", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Configuração Afiliado"
        verbose_name_plural = "Configurações Afiliados"
        
    def __str__(self) -> str:
        return f"Configuração Afiliado"
        
    def desactive_others(self):
        config = Config.objects.last()
        if config:
            config.affiliate = self
            config.save()
        AffiliateConfig.objects.exclude(id=self.id).delete()
        