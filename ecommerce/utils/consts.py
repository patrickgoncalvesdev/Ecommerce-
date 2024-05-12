from django.db import models


class VerificationType(models.TextChoices):
    REGISTER = 'REGISTER', 'Registro'
    UPDATE_PERFIL = 'UPDATE_PERFIL', 'Atualização de Perfil'
    RECOVERY_PASSWORD = 'RECOVERY_PASSWORD', 'Recuperação de Senha'
    
class PuleType(models.TextChoices):
    EACH = 'EACH', 'Cada'
    ALL = 'ALL', 'Todos'
    
class MoneyMovimentType(models.TextChoices):
    DEBIT = 'DEBIT', 'Débito'
    CREDIT = 'CREDIT', 'Crédito'
    WITHDRAW = 'WITHDRAW', 'Saque'
    DEPOSIT = 'DEPOSIT', 'Depósito'
    COMMISSION = 'COMMISSION', 'Comissão'
    BONUS = 'BONUS', 'Bônus'
    BONUS_DEBIT = 'BONUS_DEBIT', 'Débito de Bônus'
    
class MoneyMovimentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pendente'
    APPROVED = 'APPROVED', 'Aprovado'
    REPROVED = 'REPROVED', 'Reprovado'
    CANCELED = 'CANCELED', 'Cancelado'
    
class CommissionEnum(models.TextChoices):
    LIQUID = "LIQUID", "Líquido"
    GROSS = "GROSS", "Bruto"