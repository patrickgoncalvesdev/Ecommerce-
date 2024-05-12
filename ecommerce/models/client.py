from django.db import models
from ecommerce.models.user import UserAPI
from ecommerce.models.affiliate import Affiliate


class Client(UserAPI):
    associated_affiliate = models.ForeignKey(Affiliate, on_delete=models.PROTECT, blank=True, null=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        