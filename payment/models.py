from decimal import Decimal
import uuid
from django.db import models
from django.utils import timezone
from payment.consts import PaymentStatus, PaymentTypeChoices
from ecommerce.utils.consts import MoneyMovimentType
from bson import ObjectId
from ecommerce.models import Transaction
from payment.utils import validate_pix_key
from ecommerce.utils.wallet import truncate
from ecommerce.models.config import Config
from django.core.validators import MinValueValidator
from django.db import transaction

# Create your models here.


class PaymentConfigTable(models.Model):
    max_deposit_value = models.FloatField(default=1000)
    min_deposit_value = models.FloatField(default=1)

    withdraw_auto_approve = models.BooleanField(default=False)

    max_auto_withdraw_value = models.FloatField(default=1000)
    min_auto_withdraw_value = models.FloatField(default=1)

    max_withdraw_value = models.FloatField(default=1000)
    min_withdraw_value = models.FloatField(default=1)

    max_withdraw_value_per_day = models.FloatField(default=1000)
    max_withdraw_count_per_day = models.IntegerField(default=10)

    def deposit_value_is_valid(self, value):
        if value > self.max_deposit_value or value < self.min_deposit_value:
            return False
        return True

    def withdraw_value_is_valid(self, value):
        if value > self.max_withdraw_value or value < self.min_withdraw_value:
            return False
        return True

    @classmethod
    def get_config(cls):
        return cls.objects.get_or_create(id=1)[0]

    def verify_if_user_can_create_a_withdraw_request(self, withdraw_value: float, user):
        today_withdraws = WithDrawRequest.objects.filter(
            user=user,
            created_at__date=timezone.now().date(),
            status__in=[PaymentStatus.PENDING, PaymentStatus.APPROVED],
        )
        print(today_withdraws)
        print(today_withdraws.count())
        total_today_withdraw_value = today_withdraws.aggregate(models.Sum("value"))[
            "value__sum"
        ]
        if today_withdraws.count() >= self.max_withdraw_count_per_day:
            return False
        if total_today_withdraw_value is None:
            total_today_withdraw_value = 0
        if (
            total_today_withdraw_value + withdraw_value
            > self.max_withdraw_value_per_day
        ):
            return False

        return True

    class Meta:
        verbose_name = "Configuração de pagamento"
        verbose_name_plural = "Configurações de pagamento"


class PaymentOrder(models.Model):

    user = models.ForeignKey("ecommerce.UserAPI", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    type = models.CharField(
        max_length=20,
        choices=PaymentTypeChoices.choices,
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("1.00"))]
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_id = models.CharField(max_length=512, blank=True, null=True)
    integration_order_id = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.order_id} - {self.value}"

    def __generate_order_id(self):
        return str(ObjectId()) + str(uuid.uuid4())

    def save(self, *args, **kwargs):
        if not self.id:
            self.order_id = self.__generate_order_id()
        return super().save(*args, **kwargs)

    def to_order_approved(self):
        with transaction.atomic():
            if self.status == PaymentStatus.APPROVED:
                return
            self.status = PaymentStatus.APPROVED
            self.payment_date = timezone.now()
            self.user.wallet
            Transaction.new_deposit_transaction(
                value=Decimal(self.value), wallet=self.user.wallet
            )
            if not Transaction.objects.filter(
                wallet__user=self.user, type=MoneyMovimentType.DEPOSIT
            ).exists() and hasattr(self.user, "associated_affiliate"):
                if self.user.associated_affiliate:
                    config_general = Config.objects.last()
                    value = (
                        self.value
                        if self.value <= config_general.deposit.value
                        else config_general.deposit.value
                    )
                    value_bonus = value * config_general.deposit.percent / 100
                    Transaction.new_bonus_transaction(
                        value=truncate(value_bonus), wallet=self.user.wallet
                    )
            self.save()

    class Meta:
        verbose_name = "Pedido de deposito"
        verbose_name_plural = "Pedidos de deposito"
        ordering = ["-created_at"]


class WithDrawRequest(models.Model):
    user = models.ForeignKey("ecommerce.UserAPI", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("1.00"))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pix_key = models.CharField(max_length=255, validators=[validate_pix_key])
    request_id = models.CharField(max_length=512, unique=True, blank=True)
    integration_request_id = models.CharField(max_length=255, blank=True, null=True)
    money_transaction = models.ForeignKey(
        "ecommerce.Transaction", on_delete=models.PROTECT, null=True, blank=True
    )
    updated_by = models.ForeignKey(
        "ecommerce.AdministrativeUser",
        on_delete=models.SET_NULL,
        related_name="updated_withdraw_requests",
        null=True,
        blank=True,
    )

    def __generate_request_id(self):
        return str(ObjectId()) + str(uuid.uuid4())

    def save(self, *args, **kwargs):
        if not self.id:
            self.request_id = self.__generate_request_id()
        return super().save(*args, **kwargs)

    def to_order_approved(self):
        if self.status != PaymentStatus.PENDING:
            raise Exception(f"Status must be {PaymentStatus.PENDING}")
        self.status = PaymentStatus.APPROVED
        self.save()

    def make_withdraw_integration_request(self):
        # TODO implementar com a pagarme
        self.to_order_approved()
        print("Making withdraw integration request")
        # ...

    def to_order_canceled(self):
        if self.status == PaymentStatus.APPROVED:
            self.money_transaction.refund_transaction()
            self.money_transaction.save()
        self.status = PaymentStatus.CANCELED
        self.save()

    @classmethod
    def get_pending_withdraws(cls):
        return cls.objects.filter(status=PaymentStatus.PENDING)

    class Meta:
        verbose_name = "Solicitação de saque"
        verbose_name_plural = "Solicitações de saque"
        ordering = ["-created_at"]
