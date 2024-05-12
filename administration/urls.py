from django.urls import path
from django.contrib.auth.decorators import login_required

from administration.views import (
    AffiliateRegisterWithCodeView,
    AffiliateBonusEditView,
    AffiliateEditView,
    AffiliateRegisterListView,
    AffiliateView,
    AwardView,
    BackofficeLoginView,
    BackofficeLogoutView,
    ChangePasswordView,
    AffiliateAddView,
    GeneralView,
    LotteryDrawBetsReportView,
    LotteryDrawView,
    ManagerEditView,
    ManagerUserAddView,
    ManagerView,
    ModalitiesView,
    ModalityUpdateView,
    NewAffiliateRegisterLinkView,
    PLayerBonusEditView,
    PlayerAwardView,
    PlayerView,
    SupervisorEditView,
    SupervisorUserAddView,
    SupervisorView,
    TicketView,
    WithDrawChangeStatusView,
    WithDrawRequestView,
)


urlpatterns = [
    path("login/", BackofficeLoginView.as_view(), name="backoffice_login"),
    path(
        "logout/",
        login_required(BackofficeLogoutView.as_view()),
        name="backoffice_logout",
    ),
    path(
        "change_password/",
        login_required(ChangePasswordView.as_view()),
        name="backoffice_change_password",
    ),
    path("general/", login_required(GeneralView.as_view()), name="backoffice_general"),
    path(
        "affiliates/",
        login_required(AffiliateView.as_view()),
        name="affiliates",
    ),
    path(
        "affiliates/add",
        login_required(AffiliateAddView.as_view()),
        name="affiliate_add",
    ),
    path(
        "affiliates/<int:pk>",
        login_required(AffiliateEditView.as_view()),
        name="affiliate_edit",
    ),
    path(
        "affiliates/<int:pk>/bonus",
        login_required(AffiliateBonusEditView.as_view()),
        name="affiliate_bonus",
    ),
    path(
        "affiliates/generated_links",
        login_required(AffiliateRegisterListView.as_view()),
        name="affiliate_register_links",
    ),
    path(
        "affiliates/generated_links/new",
        login_required(NewAffiliateRegisterLinkView.as_view()),
        name="new_affiliate_register_link",
    ),
    path("managers/", login_required(ManagerView.as_view()), name="managers"),
    path(
        "managers/add", login_required(ManagerUserAddView.as_view()), name="manager_add"
    ),
    path(
        "managers/<int:pk>",
        login_required(ManagerEditView.as_view()),
        name="manager_edit",
    ),
    path("supervisors/", login_required(SupervisorView.as_view()), name="supervisors"),
    path(
        "supervisors/add",
        login_required(SupervisorUserAddView.as_view()),
        name="supervisor_add",
    ),
    path(
        "supervisors/<int:pk>",
        login_required(SupervisorEditView.as_view()),
        name="supervisor_edit",
    ),
    path("players/", login_required(PlayerView.as_view()), name="players"),
    path(
        "players/<int:pk>/awards",
        login_required(PlayerAwardView.as_view()),
        name="player_awards",
    ),
    path(
        "players/<int:pk>/bonus",
        login_required(PLayerBonusEditView.as_view()),
        name="player_bonus",
    ),
    path(
        "withdraw_requests/",
        login_required(WithDrawRequestView.as_view()),
        name="withdraw_requests",
    ),
    path(
        "withdraw_requests/<int:pk>/status/<str:status>",
        login_required(WithDrawChangeStatusView.as_view()),
        name="withdraw_request_state_edit",
    ),
    path(
        "modalities_configuration/",
        login_required(ModalitiesView.as_view()),
        name="modalities_configuration",
    ),
    path(
        "modalities_configuration/<int:pk>/edit",
        login_required(ModalityUpdateView.as_view()),
        name="modality_edit",
    ),
    path("awards/", login_required(AwardView.as_view()), name="awards"),
    path("tickets/", login_required(TicketView.as_view()), name="tickets"),
    path(
        "affiliates/register_with_code/",
        AffiliateRegisterWithCodeView.as_view(),
        name="affiliate_register_with_code",
    ),
    path(
        "lottery_draws/",
        login_required(LotteryDrawView.as_view()),
        name="lottery_draws",
    ),
    path(
        "lottery_draws/<int:pk>/bets/report",
        login_required(LotteryDrawBetsReportView.as_view()),
        name="lottery_draw_report",
    ),
]
