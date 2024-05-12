import os
from uuid import UUID
import uuid
import httpx
from payment.integrations.mercado_pago.schemas import (
    MercadoPagoPaymentData,
    MercadoPagoPaymentDetailResponse,
    MercadoPagoPaymentResponse,
)


class MercadoPagoPaymentAdapter:

    def __init__(self):
        self.__base_url = "https://api.mercadopago.com/v1"

    def __make_payment_request(
        self, idempotency_key: UUID, payment_data: MercadoPagoPaymentData
    ) -> dict:
        headers = {
            "X-Idempotency-Key": str(idempotency_key),
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('MERCADO_PAGO_ACCESS_TOKEN')}",
        }
        with httpx.Client() as client:
            response = client.post(
                f"{self.__base_url}/payments",
                headers=headers,
                json=payment_data.model_dump(),
            )
            response.raise_for_status()
            return response.json()

    def payment(self, payment_data: dict):
        try:
            payment_payload_validated = MercadoPagoPaymentData(**payment_data)
            idempotency_key = uuid.uuid4()
            try:
                response = self.__make_payment_request(
                    idempotency_key, payment_payload_validated
                )
            except httpx.HTTPStatusError as e:
                print(f"Error making payment: {e.response.json()}")
                raise e
            transaction_data = response["point_of_interaction"]["transaction_data"]
            return MercadoPagoPaymentResponse(
                id=str(response["id"]),
                qr_code=transaction_data["qr_code"],
                qr_code_base64=transaction_data["qr_code_base64"],
                request_key=str(idempotency_key),
            )
        except Exception as e:
            print(f"Error making payment: {e}, type: {type(e)}")
            raise e

    def validate_payment_status(self, payment_id: int):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('MERCADO_PAGO_ACCESS_TOKEN')}",
        }
        with httpx.Client() as client:
            response = client.get(
                f"{self.__base_url}/payments/{payment_id}",
                headers=headers,
            )
            response.raise_for_status()
            response_data = response.json()
            return MercadoPagoPaymentDetailResponse(
                id=str(response_data["id"]),
                status=response_data["status"],
            )
