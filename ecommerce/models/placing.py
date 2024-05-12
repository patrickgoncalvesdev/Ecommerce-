from django.db import models


class Placing(models.Model):
    name = models.CharField(max_length=255)
    award_range = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Colocação"
        verbose_name_plural = "Colocações"
    
    def __str__(self) -> str:
        return self.name
    