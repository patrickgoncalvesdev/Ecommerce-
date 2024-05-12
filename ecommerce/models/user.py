from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from ecommerce.models.wallet import Wallet


class UserAPI(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)
    cpf = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE, null=True, blank=True, related_name="user")
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="userapi_set",
        related_query_name="userapi",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="userapi_set",
        related_query_name="userapi",
    )
    is_active = models.BooleanField(default=False)
    quotation = models.ForeignKey("Quotation", on_delete=models.CASCADE, null=True, blank=True, related_name="user") # TODO Retirar o blank True null True
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
    