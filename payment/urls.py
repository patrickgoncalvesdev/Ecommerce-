from django.urls import path
from payment.views import DepositView, WebhookView, WithDrawView,PendingWithDrawView

urlpatterns = [
    path("webhook", WebhookView.as_view(), name="payment_webhook"),
    path("withdraw", WithDrawView.as_view(), name="withdraw_view"),
    path("deposit", DepositView.as_view(), name="deposit_view"),
    path("pending",PendingWithDrawView.as_view(), name="pending_view")
]
