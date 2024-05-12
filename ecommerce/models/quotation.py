from django.db import models
from ecommerce.utils.mixins import TimestampMixin


class Quotation(TimestampMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)
    modalities = models.ManyToManyField(
        "Modality", related_name="quotations", through="QuotationModality"
    )
    affiliates = models.ManyToManyField(
        "Affiliate", related_name="quotations", through="AffiliateQuotation"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Cotação"
        verbose_name_plural = "Cotações"
