from django.contrib import admin
from ecommerce.models.client import Client
from ecommerce.models.affiliate import Affiliate
from ecommerce.models.wallet import Wallet
from ecommerce.models.verification import Verification
from ecommerce.models.lottery import Lottery
from ecommerce.models.modality import Modality
from ecommerce.models.placing import Placing
from ecommerce.models.lottery_draw import LotteryDraw
from ecommerce.models.pule import Pule
from ecommerce.models.bet import Bet
from ecommerce.models.money_moviment import MoneyMoviment
from ecommerce.models.transaction import Transaction
from ecommerce.models.messages import MessagesTemplate
from ecommerce.models.administration import AdministrativeUser
from ecommerce.models.affiliate_quotation import AffiliateQuotation
from ecommerce.models.quotation_modality import QuotationModality
from ecommerce.models.quotation import Quotation
from ecommerce.models.first_deposit import FirstDeposit
from ecommerce.models.affiliate_config import AffiliateConfig
from ecommerce.models.config import Config
from django.db import models
from tinymce.widgets import TinyMCE
from django.contrib.auth.admin import UserAdmin


class MessagesTemplateAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": TinyMCE},
    }


class LotteryDrawAdmin(admin.ModelAdmin):
    change_form_template = "ecommerce/draw_custom_form.html"


class PuleAdmin(admin.ModelAdmin):
    list_display = ["hash", "lottery_draw", "win", "user", "value_total", "created_at"]
    search_fields = [
        "hash",
        "lottery_draw__name",
        "user__name",
        "user__email",
        "user__cpf",
    ]
    list_per_page = 50


class BetAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "guess",
        "win",
        "modality_name",
    ]
    search_fields = [
        "pule__hash",
        "user__name",
        "guess",
        "win",
        "draw_date",
        "modality_name",
    ]
    list_per_page = 10


class AdministrativeUserAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "wallet",
                    "profile",
                    "parent",
                    "date_joined",
                ),
            },
        ),
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "date_joined",
                ),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Supervision",
            {
                "fields": ("profile", "parent", "percent"),
            },
        ),
    )


class AffiliateAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "commission"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    list_per_page = 10


admin.site.register(Client)
admin.site.register(Affiliate, AffiliateAdmin)
admin.site.register(Wallet)
admin.site.register(Verification)
admin.site.register(Lottery)
admin.site.register(Modality)
admin.site.register(Placing)
admin.site.register(LotteryDraw, LotteryDrawAdmin)
admin.site.register(Pule, PuleAdmin)
admin.site.register(Bet, BetAdmin)
admin.site.register(MoneyMoviment)
admin.site.register(MessagesTemplate, MessagesTemplateAdmin)
admin.site.register(Transaction)
admin.site.register(AdministrativeUser, AdministrativeUserAdmin)
admin.site.register(AffiliateQuotation)
admin.site.register(Quotation)
admin.site.register(QuotationModality)
admin.site.register(FirstDeposit)
admin.site.register(Config)
admin.site.register(AffiliateConfig)
