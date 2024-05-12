from typing import Any
from django import forms
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.template.response import TemplateResponse
from administration.admin.base import (
    AdministrationAdminBase,
    AdminstrationAdminFormBase,
)
from administration.front_objects import Card
from ecommerce.models.administration import AdministrativeUser, NonAdministrativeUsers
from ecommerce.models.affiliate import Affiliate
from django.contrib import admin
import random


class AffiliateForm(AdminstrationAdminFormBase):

    def __init__(self, *args, **kwargs):
        super(AffiliateForm, self).__init__(*args, **kwargs)
        possible_parents = self.current_user.get_possible_parents_to_user(
            NonAdministrativeUsers.AFFILIATE
        )
        if possible_parents.count() == 1:
            self.fields["user_above"].initial = possible_parents.first()
            self.fields["user_above"].widget = forms.HiddenInput()
        self.fields["user_above"].queryset = (
            self.current_user.get_possible_parents_to_user(
                NonAdministrativeUsers.AFFILIATE
            )
        )
        self.fields["user_above"].initial = self.current_user

    class Meta:
        model = Affiliate
        fields = [
            "name",
            "phone",
            "email",
            "cpf",
            "quotation",
            "commission",
            "user_above",
        ]


class AffiliateAdmin(AdministrationAdminBase):
    list_display = ["name", "sells", "total_commissions", "prizes", "total", "activity"]
    search_fields = ["first_name", "last_name", "email", "username"]
    list_per_page = 10
    form = AffiliateForm

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        current_user: "AdministrativeUser" = request.user
        return (
            super()
            .get_queryset(request)
            .filter(user_above__in=current_user.get_descendants(include_self=True))
        )

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, str] | None = ...
    ) -> TemplateResponse:
        cards = [
            Card(
                title="Entradas",
                subtitle="Total de Entradas",
                content="R$ 100",
                bootstrap_class="card text-white bg-primary mb-3",
                style="max-width: 18rem;",
            ),
            Card(
                title="Saídas",
                subtitle="Total de Saídas",
                content="R$ 100",
                bootstrap_class="card text-white bg-danger mb-3",
                style="max-width: 18rem;",
            ),
            Card(
                title="Comissão",
                subtitle="Total de Comissão",
                content="R$ 100",
                bootstrap_class="card text-white bg-success mb-3",
                style="max-width: 18rem;",
            ),
            Card(
                title="Total",
                subtitle="Total de Saldo",
                content="R$ 100",
                bootstrap_class="card text-white bg-info mb-3",
                style="max-width: 18rem;",
            ),
        ]
        extra_context = {"cards": cards}
        return super(AffiliateAdmin, self).changelist_view(request, extra_context)

    @admin.display(description="Comissão")
    def total_commissions(self, obj: "Affiliate"):
        # TODO MOCKADO
        value = random.randint(0, 1000)
        return f"R$ {value},00"

    @admin.display(description="Comissão Total")
    def sells(self, obj: "Affiliate"):
        # TODO MOCKADO
        value = random.randint(0, 1000)
        return f"R$ {value},00"

    @admin.display(description="Gerente")
    def supervisor(self, obj: "Affiliate"):
        # TODO MOCKADO
        return obj.parent

    @admin.display(description="Prêmios")
    def prizes(self, obj: "Affiliate"):
        # TODO MOCKADO
        value = random.randint(0, 1000)
        return f"R$ {value},00"

    @admin.display(description="Total")
    def total(self, obj: "Affiliate"):
        # TODO MOCKADO
        value = random.randint(0, 1000)
        return f"R$ {value},00"

    @admin.display(description="Atividade")
    def activity(self, obj: "Affiliate"):
        # TODO MOCKADO
        value = random.randint(0, 10)
        return f"{value} dias atrás"

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("ecommerce.bo_admin_view_affiliate")

    def has_add_permission(self, request):
        return request.user.has_perm("ecommerce.bo_admin_add_affiliate")

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("ecommerce.bo_admin_change_affiliate")

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm("ecommerce.bo_admin_delete_affiliate")
