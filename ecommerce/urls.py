from django.urls import path
from ecommerce.apis.register import RegisterAPI
from rest_framework_simplejwt.views import TokenRefreshView
from ecommerce.apis.perfil import PerfilAPI
from ecommerce.apis.login import LoginAPIView
from ecommerce.apis.active_verfication import VerificationAPI
from ecommerce.apis.resend_code import ResendCodeRegisterAPI
from ecommerce.apis.lottery import LotteryAPI
from ecommerce.apis.cart import CartAPI, CartWithIdAPI
from ecommerce.apis.finalize_purchase import FinalizePurchaseAPI
from ecommerce.apis.pule_report import PuleReportAPI
from ecommerce.apis.days_pule_report import DaysPuleReportAPI
from ecommerce.apis.statement_report import StatementReportAPI
from ecommerce.apis.days_statement_report import DaysStatementReportAPI
from ecommerce.apis.quotes_affiliate import QuotesAffiliateAPI, QuotesAffiliateReportAPI, DownloadQuotesAffiliateReportAPI
from ecommerce.apis.quotes_user import QuotesUserDetailReportAPI
from ecommerce.apis.pule_user import PulesUserAPI
from ecommerce.apis.result import ResultAPI
from ecommerce.apis.award_history import AwardHistoryAPI
from ecommerce.apis.download_finalizae_purchase import DownloadFinalizePurchaseAPI
from ecommerce.apis.recovery import RecoveryPasswordAPI
from ecommerce.apis.wallet import WalletDataAPI
from ecommerce.apis.worth import WorthAPI
from ecommerce.apis.register_affiliate import RegisterAffiliateAPI


urlpatterns = [
    path("worth/", WorthAPI.as_view(), name="worth"),
    path("register-affiliate/", RegisterAffiliateAPI.as_view(), name="register_affiliate"),
    path("download-finalize-purchase/<str:id>", DownloadFinalizePurchaseAPI.as_view(), name="download_finalize_purchase"),
    path("download-quotes-affiliate-report/", DownloadQuotesAffiliateReportAPI.as_view(), name="download_quotes_affiliate_report"),
    path("register/", RegisterAPI.as_view(), name="register"),
    path("recovery-password/", RecoveryPasswordAPI.as_view(), name="recovery_password"),
    path("token/", LoginAPIView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("perfil/", PerfilAPI.as_view(), name="perfil"),
    path(
        "active-verification/<str:token>/",
        VerificationAPI.as_view(),
        name="active_verification",
    ),
    path(
        "resend-code/register/",
        ResendCodeRegisterAPI.as_view(),
        name="resend_code_register",
    ),
    path("lottery/", LotteryAPI.as_view(), name="lottery"),
    path("cart/", CartAPI.as_view(), name="cart"),
    path("cart/<int:id>/", CartWithIdAPI.as_view(), name="cart_delete_item"),
    path("finalize-purchase/", FinalizePurchaseAPI.as_view(), name="finalize_purchase"),
    path("report/pules/", PuleReportAPI.as_view(), name="pule_report"),
    path("report/days-pules/", DaysPuleReportAPI.as_view(), name="days_pule_report"),
    path("report/statement/", StatementReportAPI.as_view(), name="statement_report"),
    path(
        "report/days-statement/",
        DaysStatementReportAPI.as_view(),
        name="days_statement_report",
    ),
    path("user/report/quotes/", QuotesUserDetailReportAPI.as_view(), name="user_quotes_report"),
    path("affiliate/quotes/", QuotesAffiliateAPI.as_view(), name="affiliate_quotes"),
    path("affiliate/report/quotes/", QuotesAffiliateReportAPI.as_view(), name="affiliate_quotes_report"),
    path("pules/", PulesUserAPI.as_view(), name="pules_user"),
    path("result/", ResultAPI.as_view(), name="result"),
    path("award-history/", AwardHistoryAPI.as_view(), name="award_history"),
    path("wallet/", WalletDataAPI.as_view(), name="wallet_data"),
]
