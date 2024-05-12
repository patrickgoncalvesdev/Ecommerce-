from pydantic import BaseModel

from payment.integrations.mercado_pago.consts import (
    MercadoPagoPaymentMethodID,
    MercadoPagoPaymentStatus,
)


class MercadoPagoPhone(BaseModel):
    area_code: int
    number: str


class MercadoPagoIdentification(BaseModel):
    type: str
    number: str


class MercadoPagoPayerInfo(BaseModel):
    first_name: str
    last_name: str
    phone: MercadoPagoPhone


class MercadoPagoAdditionalInfo(BaseModel):
    payer: MercadoPagoPayerInfo


class MercadoPagoPayer(BaseModel):
    entity_type: str
    type: str
    email: str
    identification: MercadoPagoIdentification


class MercadoPagoPaymentData(BaseModel):
    additional_info: MercadoPagoAdditionalInfo
    description: str
    payer: MercadoPagoPayer
    payment_method_id: MercadoPagoPaymentMethodID
    transaction_amount: float
    installments: int = 1


class MercadoPagoPaymentResponse(BaseModel):
    id: str
    qr_code: str
    qr_code_base64: str
    request_key: str


class MercadoPagoPaymentDetailResponse(BaseModel):
    id: str
    status: MercadoPagoPaymentStatus


