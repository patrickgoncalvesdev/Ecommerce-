from django.db import models


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pendente"
    APPROVED = "APPROVED", "Aprovado"
    CANCELED = "CANCELED", "Cancelado"


class PaymentTypeChoices(models.TextChoices):
    PIX = "PIX", "Pix"
    CREDIT_CARD = "CREDIT_CARD", "Credit Card"
    BOLETO = "BOLETO", "Boleto"


class WithDrawStatus(models.TextChoices):
    PENDING = "PENDING", "Pendente"
    APPROVED = "APPROVED", "Aprovado"
    CANCELED = "CANCELED", "Cancelado"
