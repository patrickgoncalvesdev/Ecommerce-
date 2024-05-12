from django.db import models


class Config(models.Model):
    deposit = models.ForeignKey('FirstDeposit', on_delete=models.CASCADE)
    affiliate = models.ForeignKey('AffiliateConfig', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"
        
    def __str__(self):
        return f"Configuração"
    
    def desactive_others(self):
        Config.objects.exclude(id=self.id).delete()
        