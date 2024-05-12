from django.db import models


class QuotationModality(models.Model):
    modality = models.ForeignKey("Modality", on_delete=models.CASCADE, related_name="modality_quotations")
    quotation = models.ForeignKey("Quotation", on_delete=models.CASCADE, related_name="quotation_modalities")
    #placing = models.ForeignKey("Placing", on_delete=models.CASCADE, related_name="placing_quotations")
    multiplier = models.DecimalField(max_digits=10, decimal_places=2, default=4)

    class Meta:
        verbose_name = "Configuração da Premiação"
        verbose_name_plural = "Configurações das Premiações"
        unique_together = ("modality", "quotation")
    
    def __str__(self) -> str:
        return f"{self.quotation.name} - {self.modality.name}"
    
    @property
    def modality_name(self) -> str:
        return self.modality.name
    
    @property
    def placing_name(self) -> str:
        return self.placing.name
    