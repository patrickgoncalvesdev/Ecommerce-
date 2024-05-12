from enum import Enum


class MercadoPagoPaymentMethodID(str, Enum):
    PIX = "pix"


class MercadoPagoPaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    AUTHORIZED = "authorized"
    IN_PROCESS = "in_process"
    IN_MEDIATION = "in_mediation"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    CHARGED_BACK = "charged_back"



    