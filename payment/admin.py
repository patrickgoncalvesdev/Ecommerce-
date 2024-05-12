from django.contrib import admin

from django.db.models.query import QuerySet
from payment.models import PaymentConfigTable, PaymentOrder, WithDrawRequest




class WithdrawAdmin(admin.ModelAdmin):
    list_display = ["user", "value", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__email", "user__username", "user__cpf"]

    @admin.action(description="Cancelar saque manualmente")
    def manual_withdraw_request_cancel(
        self, request, queryset: QuerySet[WithDrawRequest]
    ):
        try:
            for withdraw in queryset:
                withdraw.to_order_canceled()
            self.message_user(request, "Saque cancelado com sucesso", "success")
        except Exception as e:
            self.message_user(request, f"Erro ao cancelar saque: {e}", "error")

    @admin.action(description="Aprovar pagamento do saque manualmente")
    def manual_withdraw_request_aprovement(
        self, request, queryset: QuerySet[WithDrawRequest]
    ):
        try:
            for withdraw in queryset:
                withdraw.make_withdraw_integration_request()
            self.message_user(request, "Saque aprovado com sucesso", "success")
        except Exception as e:
            self.message_user(request, f"Erro ao aprovar saque: {e}", "error")


    actions = [manual_withdraw_request_aprovement, manual_withdraw_request_cancel]


admin.site.register(PaymentOrder)
admin.site.register(WithDrawRequest, WithdrawAdmin)
admin.site.register(PaymentConfigTable)
