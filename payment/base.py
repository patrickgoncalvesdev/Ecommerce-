from ecommerce.models.user import UserAPI
from payment.consts import PaymentTypeChoices
from payment.integrations.mercado_pago.adapter import MercadoPagoPaymentAdapter
from payment.integrations.mercado_pago.consts import MercadoPagoPaymentStatus
from payment.models import PaymentOrder


class PaymentBaseClass:

    __payment_integration_adapter = MercadoPagoPaymentAdapter

    def create_order(self, user: UserAPI, value: float, type: PaymentTypeChoices):
        return PaymentOrder.objects.create(user=user, value=value, type=type)

    def pix_payment_request(
        self, user: UserAPI, value: float, type: PaymentTypeChoices
    ):
        order = self.create_order(user, value, type)
        payment_data = {
            "additional_info": {
                "payer": {
                    "first_name": order.user.username,
                    "last_name": "",
                    "phone": {
                        "area_code": order.user.phone[0:2],
                        "number": order.user.phone[2:],
                    },
                }
            },
            "description": "Deposit Payment",
            "installments": 1,
            "payer": {
                "entity_type": "individual",
                "type": "customer",
                "email": order.user.email,
                "identification": {"type": "CPF", "number": order.user.cpf},
            },
            "payment_method_id": "pix",
            "transaction_amount": value,
            "external_reference": order.order_id,
        }
        response = self.__payment_integration_adapter().payment(
            payment_data=payment_data
        )
        order.integration_order_id = response.id
        order.save()
        return response

    def validate_payment(self, payment_id: str):
        payment_status = self.__payment_integration_adapter().validate_payment_status(
            payment_id=payment_id
        )
        payment_order = PaymentOrder.objects.get(integration_order_id=payment_id)
        if payment_status.status == MercadoPagoPaymentStatus.APPROVED:
            payment_order.to_order_approved()
