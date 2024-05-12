from decimal import Decimal
from typing import Any
from django.db.models.query import QuerySet
from django.forms import ValidationError
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView, ListView, UpdateView
from django.views import View
from administration.filters import (
    AdministrationFilter,
    AffiliateFilter,
    LotteryDrawFilter,
    ManagerFilter,
    ModalityFilter,
    PlayerFilter,
    PuleFilter,
    WithDrawRequestFilter,
)
from bson import ObjectId
from administration.forms import (
    AdministrativeUserCreateForm,
    AdministrativeUserEditForm,
    AffiliateForm,
    BackofficeLoginForm,
    AffiliateEditForm,
    ChangePasswordForm,
    ModalityForm,
    NewAffiliateLinkForm,
    RegisterAffiliateForm,
    WithDrawRequestForm,
)
from administration.models import AffiliateRegisterInstance
from ecommerce.models.lottery_draw import LotteryDraw
from ecommerce.utils.wallet import truncate
from ecommerce.models import AdministrativeUser
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect, get_object_or_404
from ecommerce.models.administration import AdministrativeProfile
from ecommerce.models.affiliate import Affiliate
from ecommerce.models.affiliate_quotation import AffiliateQuotation
from ecommerce.models.client import Client
from ecommerce.models.modality import Modality
from ecommerce.models.pule import Pule
from ecommerce.models.transaction import Transaction
from payment.models import WithDrawRequest
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404, HttpResponse
from datetime import datetime, time
from django.contrib.auth.hashers import make_password

# Create your views here.


class BackofficeLoginView(FormView):
    form_class = BackofficeLoginForm
    template_name = "pages/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("backoffice_general")
        return super().get(request)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                next_url = request.GET.get("next", "backoffice_general")
                return redirect(next_url)
            form.add_error(None, "Usuário ou senha inválidos")
        return render(request, "pages/login.html", {"form": form})


class BackofficeLogoutView(View):

    def get(self, request):
        logout(request)
        return redirect("backoffice_login")


class ChangePasswordView(FormView):
    template_name = "pages/change_password.html"
    form_class = ChangePasswordForm

    def form_valid(self, form):
        user: AdministrativeUser = self.request.user
        current_password = form.cleaned_data["current_password"]
        if not user.check_password(current_password):
            form.add_error("current_password", "Senha atual incorreta")
            return render(self.request, self.template_name, {"form": form})
        user.set_password(form.cleaned_data["password"])
        user.save()
        logout(self.request)
        return redirect("backoffice_login")


class DashboardView(View):

    def get(self, request):
        return render(request, "pages/dashboard.html")


class AffiliateView(UserPassesTestMixin, ListView):
    template_name = "pages/affiliates.html"
    filterset_class = AffiliateFilter
    paginate_by = 5

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_affiliates")

    def get_queryset(self) -> QuerySet[Any]:
        user: "AdministrativeUser" = self.request.user
        queryset = Affiliate.objects.filter(
            user_above__in=user.get_descendants(include_self=True)
        ).order_by("username")
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        print(queryset.first().get_all_affiliate_quotations())
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context

    # def get(self, request: "AdministrativeUser"):

    #     return render(request, "pages/affiliates.html", {"affiliates": affiliates})


class AffiliateAddView(UserPassesTestMixin, FormView):
    template_name = "pages/new_affiliate.html"
    form_class = AffiliateForm

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_edit_affiliates")

    def __init__(self):
        super().__init__()
        self.success_url = reverse("affiliates")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        new_affiliate = form.save()
        new_affiliate.set_password(form.cleaned_data["password"])
        for quotation in form.cleaned_data["quotations"]:
            AffiliateQuotation.objects.create(
                affiliate=new_affiliate, quotation=quotation
            )
        return super().form_valid(form)


class AffiliateEditView(UserPassesTestMixin, UpdateView):
    template_name = "pages/new_affiliate.html"
    form_class = AffiliateEditForm
    model = Affiliate

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_edit_affiliates")

    def __init__(self):
        super().__init__()
        self.success_url = reverse("affiliates")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        affiliate = form.save()
        if form.cleaned_data.get("password"):
            affiliate.set_password(form.cleaned_data["password"])
        AffiliateQuotation.objects.filter(affiliate=affiliate).delete()
        for quotation in form.cleaned_data["quotations"]:
            if quotation not in affiliate.quotations.all():
                AffiliateQuotation.objects.create(
                    affiliate=affiliate, quotation=quotation
                )
        return super().form_valid(form)


class AffiliateBonusEditView(UserPassesTestMixin, View):

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_edit_user_bonus")

    def post(self, request, pk):
        try:
            user: AdministrativeUser = request.user
            affiliate = Affiliate.objects.get(pk=pk)
            if (
                affiliate.user_above == request.user
                or affiliate.user_above in user.get_descendants(include_self=True)
            ):
                new_bonus_balance = Decimal(request.POST.get("bonusValue"))
                if new_bonus_balance < affiliate.wallet.bonus:
                    Transaction.new_debit_bonus_transaction(
                        affiliate.wallet.bonus - new_bonus_balance,
                        affiliate.wallet,
                        user,
                    )
                elif new_bonus_balance == affiliate.wallet.bonus:
                    pass
                else:
                    Transaction.new_bonus_transaction(
                        new_bonus_balance - affiliate.wallet.bonus,
                        affiliate.wallet,
                        user,
                    )
                print(f"Bonus: {affiliate.wallet.bonus}")
                affiliate.wallet.save()
        except Exception as e:
            print(f"Error on update bonus: {e}")
        finally:
            return redirect("affiliates")


class GeneralView(ListView):
    template_name = "pages/general.html"
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Any]:
        user: "AdministrativeUser" = self.request.user
        self.filterset = None
        if self.request.user.profile == AdministrativeProfile.MANAGER:
            queryset = Affiliate.objects.filter(user_above=user).order_by("username")
            self.filterset = AffiliateFilter(self.request.GET, queryset=queryset)
        else:
            queryset = user.get_descendants().order_by("username")
        if not self.filterset:
            self.filterset = AdministrationFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def __get_date_range_or_today(self):
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
        else:
            start_date = datetime.combine(datetime.now().date(), time.min)
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M")
        else:
            end_date = datetime.combine(datetime.now().date(), time.max)
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M")
        return {
            "start_date": start_date,
            "end_date": datetime.combine(datetime.now().date(), time.max),
            "start_date_str": start_date_str,
            "end_date_str": end_date_str,
        }

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        date_range = self.__get_date_range_or_today()

        context = context | date_range
        sells = self.request.user.sells(
            {"created_at__date__range": [context["start_date"], context["end_date"]]}
        )
        commissions = self.request.user.commissions(
            {"created_at__date__range": [context["start_date"], context["end_date"]]}
        )
        awards = self.request.user.awards(
            {"created_at__date__range": [context["start_date"], context["end_date"]]}
        )
        with_my_commissions = self.request.user.commissions_with_my(
            {"created_at__date__range": [context["start_date"], context["end_date"]]}
        )
        context["commissions_with_my"] = round(with_my_commissions, 2)
        context["in_values"] = round(sells, 2)
        context["out_values"] = round(commissions + awards, 2)
        context["comission"] = round(
            truncate(
                (sells - context["out_values"])
                * (
                    self.request.user.percent / 100
                    if self.request.user.percent
                    else Decimal(1)
                )
            ),
            2,
        )
        context["total"] = round(  # TODO ajustar calculos
            context["in_values"] - context["out_values"] - context["comission"], 2
        )

        context["users_profile"] = (
            AdministrativeProfile.get_by_str(
                self.filterset.form.cleaned_data.get("profile")
            ).label
            if self.filterset.form.cleaned_data.get("profile")
            else None
        )
        return context


class ManagerView(UserPassesTestMixin, ListView):
    template_name = "pages/managers.html"
    filterset_class = ManagerFilter
    paginate_by = 5

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_managers")

    def get_queryset(self) -> QuerySet[Any]:
        user: "AdministrativeUser" = self.request.user
        queryset = (
            user.get_descendants(include_self=True)
            .filter(profile=AdministrativeProfile.MANAGER)
            .order_by("username")
        )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class ManagerUserAddView(UserPassesTestMixin, FormView):
    template_name = "pages/new_adm_user.html"
    form_class = AdministrativeUserCreateForm

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_managers")

    def __init__(self):
        super().__init__()
        self.success_url = reverse("managers")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["new_user_profile"] = AdministrativeProfile.MANAGER
        return kwargs

    def form_valid(self, form: "AdministrativeUserCreateForm"):
        instance = form.save()
        password = make_password(form.cleaned_data["password"])
        user = AdministrativeUser.objects.get(id=instance.id)
        user.password = password
        user.save()
        return super().form_valid(form)


class ManagerEditView(UserPassesTestMixin, UpdateView):
    template_name = "pages/new_adm_user.html"
    form_class = AdministrativeUserEditForm
    model = AdministrativeUser

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_managers")

    def __init__(self):
        super().__init__()
        self.success_url = reverse("managers")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        instance = form.save()
        if form.cleaned_data.get("password"):
            instance.set_password(form.cleaned_data["password"])
        return super().form_valid(form)


class SupervisorView(UserPassesTestMixin, ListView):
    template_name = "pages/supervisors.html"
    filterset_class = ManagerFilter
    paginate_by = 5

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_supervisors")

    def get_queryset(self) -> QuerySet[Any]:
        user: "AdministrativeUser" = self.request.user
        queryset = (
            user.get_descendants(include_self=True)
            .filter(profile=AdministrativeProfile.SUPERVISOR)
            .order_by("username")
        )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class SupervisorUserAddView(UserPassesTestMixin, FormView):
    template_name = "pages/new_adm_user.html"
    form_class = AdministrativeUserCreateForm

    def __init__(self):
        super().__init__()
        self.success_url = reverse("supervisors")

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_supervisors")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["new_user_profile"] = AdministrativeProfile.SUPERVISOR
        return kwargs

    def form_valid(self, form: "AdministrativeUserCreateForm"):
        instance = form.save()
        password = make_password(form.cleaned_data["password"])
        user = AdministrativeUser.objects.get(id=instance.id)
        user.password = password
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form: "AdministrativeUserCreateForm"):
        print(form.errors)
        return super().form_invalid(form)


class SupervisorEditView(UserPassesTestMixin, UpdateView):
    template_name = "pages/new_adm_user.html"
    form_class = AdministrativeUserEditForm
    model = AdministrativeUser

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_supervisors")

    def __init__(self):
        super().__init__()
        self.success_url = reverse("supervisors")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        instance = form.save()
        if form.cleaned_data.get("password"):
            instance.set_password(form.cleaned_data["password"])
        return super().form_valid(form)


class PlayerView(UserPassesTestMixin, ListView):
    template_name = "pages/players.html"
    filterset_class = PlayerFilter
    paginate_by = 5

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_players")

    def get_queryset(self) -> QuerySet[Any]:
        user: "AdministrativeUser" = self.request.user
        queryset = user.get_descendants_players().order_by("username")

        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class PlayerAwardView(UserPassesTestMixin, ListView):
    template_name = "pages/player_awards.html"
    paginate_by = 5
    filterset_class = PuleFilter

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_awards")

    def get_queryset(self) -> QuerySet[Any]:
        player_id = self.kwargs.get("pk")
        user: "AdministrativeUser" = self.request.user
        player = get_object_or_404(Client, pk=player_id)
        if not player in user.get_descendants_players():
            print("Opa")
        queryset = Pule.objects.filter(user=player, win=True).distinct("id")
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        context["player"] = get_object_or_404(Client, pk=self.kwargs.get("pk"))
        return context


class PLayerBonusEditView(UserPassesTestMixin, View):

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_players")

    def post(self, request, pk):
        try:
            user: AdministrativeUser = request.user
            player = Client.objects.get(pk=pk)
            if user.profile == AdministrativeProfile.ADMIN or (
                player.associated_affiliate.user_above == request.user
                or player.associated_affiliate.user_above
                in user.get_descendants(include_self=True)
            ):
                new_bonus_balance = Decimal(request.POST.get("bonusValue"))
                if new_bonus_balance < player.wallet.bonus:
                    Transaction.new_debit_bonus_transaction(
                        player.wallet.bonus - new_bonus_balance,
                        player.wallet,
                        user,
                    )
                elif new_bonus_balance == player.wallet.bonus:
                    pass
                else:
                    Transaction.new_bonus_transaction(
                        new_bonus_balance - player.wallet.bonus,
                        player.wallet,
                        user,
                    )
                print(f"Bonus: {player.wallet.bonus}")
                player.wallet.save()
            else:
                print(
                    f"User {request.user.username} not allowed to update player bonus"
                )
        except Exception as e:
            print(f"Error on update bonus: {e}")
        finally:
            return redirect("players")


class WithDrawRequestView(UserPassesTestMixin, ListView):
    template_name = "pages/withdraw_requests.html"
    paginate_by = 5
    filterset_class = WithDrawRequestFilter
    form = WithDrawRequestForm

    def test_func(self) -> bool | None:
        return self.request.user.has_perm(
            "ecommerce.bo_can_view_and_edit_withdraw_requests"
        )

    def get_queryset(self) -> QuerySet[Any]:
        queryset = WithDrawRequest.objects.all().order_by("-created_at")
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset

        return context


class WithDrawChangeStatusView(UserPassesTestMixin, View):
    form = WithDrawRequestForm

    def test_func(self) -> bool | None:
        return self.request.user.has_perm(
            "ecommerce.bo_can_view_and_edit_withdraw_requests"
        )

    def get(self, request, pk: int, status: str):
        with_draw_request = WithDrawRequest.objects.get(pk=pk)
        with_draw_request.status = status
        with_draw_request.updated_by = request.user
        with_draw_request.save()
        messages.success(request, "Status atualizado com sucesso")
        return redirect("withdraw_requests")


class ModalitiesView(UserPassesTestMixin, ListView):
    template_name = "pages/modalities.html"
    paginate_by = 5
    filterset_class = ModalityFilter

    def test_func(self) -> bool | None:
        return self.request.user.has_perm(
            "ecommerce.bo_can_view_and_edit_configurations"
        )

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Modality.objects.all().order_by("-name")
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class ModalityUpdateView(UserPassesTestMixin, UpdateView):
    template_name = "pages/edit_modality.html"
    form_class = ModalityForm
    model = Modality

    def test_func(self) -> bool | None:
        return self.request.user.has_perm(
            "ecommerce.bo_can_view_and_edit_configurations"
        )

    def __init__(self):
        super().__init__()
        self.success_url = reverse("modalities_configuration")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AwardView(UserPassesTestMixin, ListView):
    template_name = "pages/awards.html"
    paginate_by = 5
    filterset_class = PuleFilter

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_awards")

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Pule.objects.filter(win=True).distinct("id")
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class TicketView(UserPassesTestMixin, ListView):
    template_name = "pages/tickets.html"
    paginate_by = 5
    filterset_class = PuleFilter

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_and_edit_awards")

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Pule.objects.all().order_by("-created_at")
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class AffiliateRegisterListView(UserPassesTestMixin, ListView):
    template_name = "pages/affiliate_register_links.html"
    paginate_by = 5

    def test_func(self) -> bool | None:
        return self.request.user.has_perm("ecommerce.bo_can_view_affiliates")

    def get_queryset(self) -> QuerySet[Any]:
        user: AdministrativeUser = self.request.user
        if user.profile == AdministrativeProfile.ADMIN:
            return AffiliateRegisterInstance.objects.all().order_by("-created_at")
        return AffiliateRegisterInstance.objects.filter(
            manager__in=user.get_descendants(include_self=True)
        ).order_by("-created_at")


class NewAffiliateRegisterLinkView(FormView):
    template_name = "pages/new_affiliate_register_link.html"
    form_class = NewAffiliateLinkForm

    def __init__(self):
        super().__init__()
        self.success_url = reverse("affiliate_register_links")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect(self.success_url)


class AffiliateRegisterWithCodeView(FormView):
    template_name = "pages/affiliate_register.html"
    form_class = RegisterAffiliateForm

    def __init__(self):
        super().__init__()
        self.success_url = "https://www.datagaming.com.br/login"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        code = self.request.GET.get("code")
        self.register_instance = AffiliateRegisterInstance.objects.get(code=code)
        try:
            if (
                self.register_instance.registrations
                >= self.register_instance.max_registrations
            ):
                messages.error(self.request, "Limite de registros atingido")
            kwargs["register_instance"] = self.register_instance
        except Exception:
            raise Exception("Código de registro inválido")
        return kwargs

    def form_valid(self, form):
        if (
            self.register_instance.registrations
            >= self.register_instance.max_registrations
        ):
            messages.error(self.request, "Limite de registros atingido")
        else:
            self.register_instance.registrations += 1
            self.register_instance.save()
            form.save()
            return redirect(self.success_url)


class LotteryDrawView(UserPassesTestMixin, ListView):
    template_name = "pages/lottery_draws.html"
    paginate_by = 5
    filterset_class = LotteryDrawFilter

    def test_func(self) -> bool | None:
        return self.request.user.has_perm(
            "ecommerce.bo_can_view_and_edit_configurations"
        )

    def get_queryset(self) -> QuerySet[Any]:
        user: "AdministrativeUser" = self.request.user
        queryset = LotteryDraw.objects.all().order_by("-date")
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class LotteryDrawBetsReportView(UserPassesTestMixin, View):

    def test_func(self) -> bool | None:
        return self.request.user.has_perm(
            "ecommerce.bo_can_view_and_edit_configurations"
        )

    def get(self, request, pk):
        lottery_draw = LotteryDraw.objects.get(pk=pk)
        data = lottery_draw.get_bets_relatory()
        print(data)
        response = HttpResponse(
            lottery_draw.get_bets_relatory(), content_type="text/plain"
        )
        response["Content-Disposition"] = f'attachment; filename="{ObjectId()}.txt"'
        return response
