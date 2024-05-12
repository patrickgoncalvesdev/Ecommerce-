from django_filters import CharFilter, FilterSet, ChoiceFilter, DateTimeFilter
from django.db.models import Q
from django.forms.widgets import Select, TextInput, DateTimeInput

from ecommerce.models.administration import AdministrativeProfile
from ecommerce.models.lottery import Lottery
from ecommerce.models.quotation import Quotation
from payment.consts import PaymentStatus


class AffiliateFilter(FilterSet):
    username = CharFilter(
        method="name_filter",
        lookup_expr="icontains",
        label="Nome de usuário",
        widget=TextInput(attrs={"class": "form-control"}),
    )
    manager = ChoiceFilter(
        field_name="user_above__id",
        label="Gerente",
        widget=Select(attrs={"class": "form-control"}),
    )
    quotation = ChoiceFilter(
        field_name="quotations",
        label="Cotação",
        widget=Select(attrs={"class": "form-control"}),
        required=False,
    )

    def name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        manager_choices = self.__get_manager_choices()
        self.filters["manager"].extra["choices"] = manager_choices
        self.filters["quotation"].extra["choices"] = self.__get_quotation_choices()

    def __get_manager_choices(self):
        managers = set(
            self.queryset.values_list("user_above__id", "user_above__username")
        )
        return managers

    def __get_quotation_choices(self):
        quotations = set(self.queryset.values_list("quotations", "quotations__name"))
        return quotations


class AdministrationFilter(FilterSet):
    username = CharFilter(
        method="name_filter",
        lookup_expr="icontains",
        label="Nome de usuário",
        widget=TextInput(attrs={"class": "form-control"}),
    )

    profile = ChoiceFilter(
        field_name="profile",
        label="Perfil",
        widget=Select(attrs={"class": "form-control"}),
        initial=AdministrativeProfile.SUPERVISOR,
    )

    def __get_profile_choices(self):

        profiles_set = set(self.queryset.values_list("profile", "profile"))
        profiles = []
        for profile in list(profiles_set):
            profile = (profile[0], AdministrativeProfile.get_by_str(profile[0]).label)
            profiles.append(profile)
        return profiles

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["profile"].extra["choices"] = self.__get_profile_choices()
        self.form.initial["profile"] = AdministrativeProfile.SUPERVISOR


class ManagerFilter(FilterSet):
    username = CharFilter(
        method="name_filter",
        lookup_expr="icontains",
        label="Nome de usuário",
        widget=TextInput(attrs={"class": "form-control"}),
    )
    supervisor = ChoiceFilter(
        field_name="parent__id",
        label="Supervisor",
        widget=Select(attrs={"class": "form-control"}),
    )

    def name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
        )

    def __get_supervisor_choices(self):
        supervisors = set(self.queryset.values_list("parent__id", "parent__username"))
        return supervisors

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        supervisor_choices = self.__get_supervisor_choices()
        self.filters["supervisor"].extra["choices"] = supervisor_choices


class PlayerFilter(FilterSet):
    username = CharFilter(
        method="name_filter",
        lookup_expr="icontains",
        label="Nome de usuário",
        widget=TextInput(attrs={"class": "form-control"}),
    )
    manager = ChoiceFilter(
        field_name="associated_affiliate__user_above__id",
        label="Gerente",
        widget=Select(attrs={"class": "form-control"}),
    )
    quotation = ChoiceFilter(
        field_name="quotation",
        label="Cotação",
        widget=Select(attrs={"class": "form-control"}),
        required=True,
    )

    def name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        manager_choices = self.__get_manager_choices()
        self.filters["manager"].extra["choices"] = manager_choices
        self.filters["quotation"].extra["choices"] = self.__get_quotation_choices()

    def __get_manager_choices(self):
        managers = set(
            self.queryset.values_list(
                "associated_affiliate__user_above__id",
                "associated_affiliate__user_above__username",
            )
        )
        return managers

    def __get_quotation_choices(self):
        return Quotation.objects.all().values_list("id", "name")


class WithDrawRequestFilter(FilterSet):
    username = CharFilter(
        method="name_filter",
        lookup_expr="icontains",
        label="Nome de usuário",
        widget=TextInput(attrs={"class": "form-control"}),
    )
    status = ChoiceFilter(
        field_name="status",
        label="Status",
        widget=Select(attrs={"class": "form-control"}),
        choices=PaymentStatus.choices,
    )

    def name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(user__username__icontains=value)
            | Q(user__first_name__icontains=value)
            | Q(user__last_name__icontains=value)
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.filters["status"].extra["choices"] = PaymentStatus.choices


class ModalityFilter(FilterSet):
    name = CharFilter(
        method="name_filter",
        lookup_expr="icontains",
        label="Nome",
        widget=TextInput(attrs={"class": "form-control"}),
    )

    def name_filter(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class PuleFilter(FilterSet):
    hash = CharFilter(
        field_name="hash",
        lookup_expr="icontains",
        label="Codigo",
        widget=TextInput(attrs={"class": "form-control"}),
    )
    lottery = ChoiceFilter(
        field_name="lottery_draw__lottery__id",
        label="Loteria",
        widget=Select(attrs={"class": "form-control"}),
    )

    initial_date = DateTimeFilter(
        field_name="lottery_draw__date",
        lookup_expr="gte",
        label="Data inicial",
        widget=DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
    )

    final_date = DateTimeFilter(
        field_name="lottery_draw__date",
        lookup_expr="lte",
        label="Data final",
        widget=DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
    )

    def get_lotery_choices(self):
        return Lottery.objects.filter(is_active=True).values_list("id", "name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["lottery"].extra["choices"] = self.get_lotery_choices()


class LotteryDrawFilter(FilterSet):
    lottery = ChoiceFilter(
        label="Loteria",
        field_name="lottery__id",
        widget=Select(attrs={"class": "form-control"}),
    )
    result = ChoiceFilter(
        method="result_is_not_null",
        label="Resultado",
        widget=Select(attrs={"class": "form-control"}),
        required=True,
    )
    initial_date = DateTimeFilter(
        field_name="date",
        lookup_expr="gte",
        label="Data inicial",
        widget=DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
    )

    final_date = DateTimeFilter(
        field_name="date",
        lookup_expr="lte",
        label="Data final",
        widget=DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
    )

    def result_is_not_null(self, queryset, name, value):
        if value == "True":
            return queryset.filter(results__isnull=False)
        return queryset

    def get_results_choices(self):
        return [(True, "Com resultado"), (False, "Sem resultado")]

    def get_lotery_choices(self):
        return Lottery.objects.filter(is_active=True).values_list("id", "name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["lottery"].extra["choices"] = self.get_lotery_choices()
        self.filters["result"].extra["choices"] = self.get_results_choices()
