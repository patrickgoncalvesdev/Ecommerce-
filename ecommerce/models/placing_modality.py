from django.db import models


class PlacingModality(models.Model):
    """SUMIR COM ESSE MODEL"""
    modality = models.ForeignKey("Modality", on_delete=models.CASCADE, related_name="modality_lotteries")
    placing = models.ForeignKey("Placing", on_delete=models.CASCADE, related_name="placing_modalities")

    class Meta:
        verbose_name = "Configuração da Modalidade e Colocação"
        verbose_name_plural = "Configurações das Modalidades e Colocações"
        unique_together = ("modality", "placing")
    
    def __str__(self) -> str:
        return f"{self.modality.name} - {self.placing.name}"
    