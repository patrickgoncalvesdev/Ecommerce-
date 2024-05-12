from django.db import models

from secrets import token_urlsafe

# Create your models here.


class AffiliateRegisterInstance(models.Model):
    manager = models.ForeignKey(
        "ecommerce.AdministrativeUser",
        on_delete=models.CASCADE,
        related_name="manager",
        verbose_name="Gerente",
    )
    code = models.CharField(
        max_length=100,
        verbose_name="Código",
        help_text="Código de registro",
        blank=True,
    )
    max_registrations = models.IntegerField(
        default=1, verbose_name="Quantidade máxima de registros"
    )
    registrations = models.IntegerField(default=0, verbose_name="Registros")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.code = token_urlsafe(16)
        super(AffiliateRegisterInstance, self).save(*args, **kwargs)
