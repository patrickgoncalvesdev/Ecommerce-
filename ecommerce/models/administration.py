import random
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager
from rest_framework import serializers
from ecommerce.models.money_moviment import MoneyMoviment
from ecommerce.models.transaction import Transaction
from ecommerce.models.wallet import Wallet
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from ecommerce.utils.consts import MoneyMovimentType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet
from ecommerce.utils.consts import CommissionEnum


class AdministrativeProfile(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    SUPERVISOR = "SUPERVISOR", "Supervisor"
    MANAGER = "MANAGER", "Gerente"

    @classmethod
    def get_by_str(cls, string: str):
        for profile in cls:
            if profile.value == string:
                return profile
        return None


class NonAdministrativeUsers(models.TextChoices):
    CLIENT = "CLIENT", "Cliente"
    AFFILIATE = "AFFILIATE", "Afiliado"


class CustomTreeUserManager(TreeManager, UserManager):
    pass


class AdministrativeUser(MPTTModel, AbstractUser):
    profile = models.CharField(max_length=20, choices=AdministrativeProfile.choices)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    wallet = models.OneToOneField(
        Wallet, on_delete=models.CASCADE, related_name="administrative_user"
    )
    commission = models.CharField(
        max_length=10, choices=CommissionEnum.choices, default=CommissionEnum.LIQUID
    )
    percent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Comissão %",
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="administrative_users",
        related_query_name="administrative_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="administrative_users",
        related_query_name="administrative_user",
    )

    objects = CustomTreeUserManager()

    backend = "administration.backends.AdminCustomAuthBackend"

    class Meta:
        verbose_name = "Usuário Administrativo"
        verbose_name_plural = "Usuários Administrativos"
        permissions = (
            ("bo_can_view_affiliates", "Can view affiliates"),
            ("bo_can_edit_affiliates", "Can edit affiliates"),
            ("bo_can_view_and_edit_managers", "Can view and edit managers"),
            ("bo_can_view_and_edit_supervisors", "Can view and edit supervisors"),
            ("bo_can_view_and_edit_players", "Can view and edit players"),
            (
                "bo_can_view_and_edit_withdraw_requests",
                "Can view and edit withdraw requests",
            ),
            ("bo_can_view_and_edit_configurations", "Can view and edit configurations"),
            ("bo_can_view_and_edit_awards", "Can view and edit awards"),
            ("bo_can_edit_user_bonus", "Can edit user bonus"),
            ("bo_can_view_and_edit_administration_commissions", "Can view and edit administrative user commissions"),
            ("bo_can_view_and_edit_affiliates_commissions", "Can view and edit affiliates commissions"),
        )

    def save(self, *args, **kwargs):
        new_user = False
        if not self.id:
            new_user = True
            self.wallet = Wallet.objects.create()
            if self.is_superuser:
                self.profile = AdministrativeProfile.ADMIN
        super().save(*args, **kwargs)
        if new_user:
            self.set_permissions_by_user_profile()

    def validate_profile(self):
        if self.profile == AdministrativeProfile.ADMIN:
            self.is_superuser = True
        else:
            if not self.user_above:
                raise serializers.ValidationError(
                    {"user_above": "Este campo é obrigatório."}
                )

    def get_possible_parents_to_user(self, user_profile: str) -> "QuerySet":
        if self.is_superuser:
            if user_profile == AdministrativeProfile.ADMIN:
                return AdministrativeUser.objects.none()
            if user_profile == AdministrativeProfile.SUPERVISOR:
                return AdministrativeUser.objects.filter(
                    profile=AdministrativeProfile.ADMIN
                )
            if user_profile == AdministrativeProfile.MANAGER:
                return AdministrativeUser.objects.filter(
                    profile=AdministrativeProfile.SUPERVISOR
                )
            if user_profile == NonAdministrativeUsers.AFFILIATE:
                return AdministrativeUser.objects.filter(
                    profile=AdministrativeProfile.MANAGER
                )
        if self.profile == AdministrativeProfile.ADMIN:
            if user_profile == AdministrativeProfile.SUPERVISOR:
                return AdministrativeUser.objects.filter(id=self.id)
            if user_profile == AdministrativeProfile.MANAGER:
                return self.get_descendants().filter(
                    profile=AdministrativeProfile.SUPERVISOR
                )
            if user_profile == NonAdministrativeUsers.AFFILIATE:
                return self.get_descendants().filter(
                    profile=AdministrativeProfile.MANAGER
                )
        if self.profile == AdministrativeProfile.SUPERVISOR:
            if user_profile == AdministrativeProfile.MANAGER:
                return AdministrativeUser.objects.filter(id=self.id)
            if user_profile == NonAdministrativeUsers.AFFILIATE:
                return self.get_descendants().filter(
                    profile=AdministrativeProfile.MANAGER
                )
        if self.profile == AdministrativeProfile.MANAGER:
            if user_profile == NonAdministrativeUsers.AFFILIATE:
                return AdministrativeUser.objects.filter(id=self.id)
        return AdministrativeUser.objects.none()

    def paid_commissions(self, filter: dict = {}):
        return 100

    def sells(self, filter: dict = {}):
        if self.profile == AdministrativeProfile.ADMIN:
            sells = MoneyMoviment.objects.filter(type=MoneyMovimentType.DEBIT, **filter)
            result = sells.aggregate(total=models.Sum("value", default=0))["total"]
        elif self.profile == AdministrativeProfile.SUPERVISOR:
            sells = MoneyMoviment.objects.filter(
                bet__pule__seller__user_above__parent=self,
                type=MoneyMovimentType.DEBIT,
                **filter,
            )
            result = sells.aggregate(total=models.Sum("value", default=0))["total"]
        elif self.profile == AdministrativeProfile.MANAGER:
            sells = MoneyMoviment.objects.filter(
                bet__pule__seller__user_above=self,
                type=MoneyMovimentType.DEBIT,
                **filter,
            )
            result = sells.aggregate(total=models.Sum("value", default=0))["total"]
        else:
            sells = MoneyMoviment.objects.filter(
                bet__pule__seller=self, type=MoneyMovimentType.DEBIT, **filter
            )
            result = sells.aggregate(total=models.Sum("value", default=0))["total"]
        return result

    def commissions(self, filter: dict = {}):
        if self.profile == AdministrativeProfile.ADMIN:
            commissions = MoneyMoviment.objects.filter(
                type=MoneyMovimentType.COMMISSION, **filter
            )
            commissions_transaction = Transaction.objects.filter(
                type=MoneyMovimentType.COMMISSION, **filter
            ).exclude(wallet__administrative_user=self)
            result = (
                commissions.aggregate(total=models.Sum("value", default=0))["total"]
                + commissions_transaction.aggregate(
                    total=models.Sum("value", default=0)
                )["total"]
            )
        elif self.profile == AdministrativeProfile.SUPERVISOR:
            commissions = MoneyMoviment.objects.filter(
                wallet__user__affiliate__user_above__parent=self,
                type=MoneyMovimentType.COMMISSION,
                **filter,
            )
            commissions_transaction = Transaction.objects.filter(
                wallet__administrative_user__parent=self,
                type=MoneyMovimentType.COMMISSION,
                **filter,
            )
            result = (
                commissions.aggregate(total=models.Sum("value", default=0))["total"]
                + commissions_transaction.aggregate(
                    total=models.Sum("value", default=0)
                )["total"]
            )
        elif self.profile == AdministrativeProfile.MANAGER:
            commissions = MoneyMoviment.objects.filter(
                wallet__user__affiliate__user_above=self,
                type=MoneyMovimentType.COMMISSION,
                **filter,
            )
            result = commissions.aggregate(total=models.Sum("value", default=0))[
                "total"
            ]
        else:
            commissions = MoneyMoviment.objects.filter(
                wallet__user=self, type=MoneyMovimentType.COMMISSION, **filter
            )
            result = commissions.aggregate(total=models.Sum("value", default=0))[
                "total"
            ]
        return result

    def awards(self, filter: dict = {}):
        if self.profile == AdministrativeProfile.ADMIN:
            awards = MoneyMoviment.objects.filter(
                type=MoneyMovimentType.CREDIT, **filter
            )
            result = awards.aggregate(total=models.Sum("value", default=0))["total"]
        elif self.profile == AdministrativeProfile.SUPERVISOR:
            awards = MoneyMoviment.objects.filter(
                bet__pule__seller__user_above__parent=self,
                type=MoneyMovimentType.CREDIT,
                **filter,
            )
            result = awards.aggregate(total=models.Sum("value", default=0))["total"]
        elif self.profile == AdministrativeProfile.MANAGER:
            awards = MoneyMoviment.objects.filter(
                bet__pule__seller__user_above=self,
                type=MoneyMovimentType.CREDIT,
                **filter,
            )
            result = awards.aggregate(total=models.Sum("value", default=0))["total"]
        else:
            awards = MoneyMoviment.objects.filter(
                bet__pule__seller=self, type=MoneyMovimentType.CREDIT, **filter
            )
            result = awards.aggregate(total=models.Sum("value", default=0))["total"]
        return result

    def total(self, filter: dict = {}):
        return self.sells(filter) - self.commissions(filter) - self.awards(filter)

    def total_with_my(self, filter: dict = {}):
        return (
            self.sells(filter) - self.commissions_with_my(filter) - self.awards(filter)
        )

    def commissions_with_my(self, filter: dict = {}):
        if self.profile == AdministrativeProfile.ADMIN:
            commissions = MoneyMoviment.objects.filter(
                type=MoneyMovimentType.COMMISSION, **filter
            )
            commissions_transaction = Transaction.objects.filter(
                type=MoneyMovimentType.COMMISSION, **filter
            ).exclude(wallet__administrative_user=self)
            my_transactions = Transaction.objects.filter(
                wallet__administrative_user=self,
                type=MoneyMovimentType.COMMISSION,
                **filter,
            )
            result = (
                commissions.aggregate(total=models.Sum("value", default=0))["total"]
                + my_transactions.aggregate(total=models.Sum("value", default=0))[
                    "total"
                ]
                + commissions_transaction.aggregate(
                    total=models.Sum("value", default=0)
                )["total"]
            )
        elif self.profile == AdministrativeProfile.SUPERVISOR:
            commissions = MoneyMoviment.objects.filter(
                wallet__user__affiliate__user_above__parent=self,
                type=MoneyMovimentType.COMMISSION,
                **filter,
            )
            commissions_transaction = Transaction.objects.filter(
                wallet__administrative_user__parent=self,
                type=MoneyMovimentType.COMMISSION,
                **filter,
            )
            my_transactions = Transaction.objects.filter(
                wallet__administrative_user=self,
                type=MoneyMovimentType.COMMISSION,
                **filter,
            )
            result = (
                commissions.aggregate(total=models.Sum("value", default=0))["total"]
                + my_transactions.aggregate(total=models.Sum("value", default=0))[
                    "total"
                ]
                + commissions_transaction.aggregate(
                    total=models.Sum("value", default=0)
                )["total"]
            )
        elif self.profile == AdministrativeProfile.MANAGER:
            commissions = MoneyMoviment.objects.filter(
                wallet__user__affiliate__user_above=self,
                type=MoneyMovimentType.COMMISSION,
                **filter,
            )
            my_transactions = Transaction.objects.filter(
                wallet__administrative_user=self,
                type=MoneyMovimentType.COMMISSION,
                **filter,
            )
            result = (
                commissions.aggregate(total=models.Sum("value", default=0))["total"]
                + my_transactions.aggregate(total=models.Sum("value", default=0))[
                    "total"
                ]
            )
        else:
            commissions = MoneyMoviment.objects.filter(
                wallet__user=self, type=MoneyMovimentType.COMMISSION, **filter
            )
            result = commissions.aggregate(total=models.Sum("value", default=0))[
                "total"
            ]
        return result

    def is_manager(self):
        return self.profile == AdministrativeProfile.MANAGER

    def is_supervisor(self):
        return self.profile == AdministrativeProfile.SUPERVISOR

    def is_admin(self):
        return self.profile == AdministrativeProfile.ADMIN

    def is_admin_staff(self):
        return self.is_admin() and self.is_staff

    def percent_str_value(self):
        if not self.percent:
            return "0%"
        return f"{self.percent}%"

    def set_permissions_by_user_profile(self):
        if self.profile == AdministrativeProfile.ADMIN:
            self.groups.set(
                [
                    Group.objects.get(name="Administrador"),
                ]
            )
        elif self.profile == AdministrativeProfile.SUPERVISOR:
            self.groups.set(
                [
                    Group.objects.get(name="Supervisor"),
                ]
            )
        elif self.profile == AdministrativeProfile.MANAGER:
            self.groups.set(
                [
                    Group.objects.get(name="Gerente"),
                ]
            )
        self.save()

    def get_descendants_players(self):
        from ecommerce.models import Client

        if self.profile == AdministrativeProfile.ADMIN:
            return Client.objects.all()
        Client.objects.filter(
            associated_affiliate__user_above__in=self.get_descendants(include_self=True)
        )
