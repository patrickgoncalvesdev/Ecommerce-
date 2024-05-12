from django.db import models
from django.utils.crypto import get_random_string


def generate_code_affiliate():
    code = get_random_string(length=4)
    if AffiliateQuotation.objects.filter(code=code).exists():
        return generate_code_affiliate()
    return code


class AffiliateQuotation(models.Model):
    code = models.CharField(default=generate_code_affiliate, max_length=4, unique=True)
    quotation = models.ForeignKey("Quotation", on_delete=models.CASCADE)
    affiliate = models.ForeignKey(
        "Affiliate", on_delete=models.CASCADE, related_name="affiliate_quotations"
    )
    percent = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Quotação por Afiliado"
        verbose_name_plural = "Quotações por Afiliados"
        unique_together = ("affiliate", "quotation")

    @property
    def name(self):
        return f"{self.quotation.name}"

    def __str__(self):
        return f"{self.quotation.name} - {self.percent}%"
