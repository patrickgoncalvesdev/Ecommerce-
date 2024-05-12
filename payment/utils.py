import re
from validate_docbr import CPF, CNPJ
from rest_framework.exceptions import ValidationError


def validate_pix_key(chave: str):
    def is_cpf_cnpj(chave):
        cpf = CPF()
        cnpj = CNPJ()
        return (len(chave) == 11 and cpf.validate(chave)) or (
            len(chave) == 14 and cnpj.validate(chave)
        )

    def is_celular(chave):
        return bool(re.match(r"^\+55\d{2}9\d{8}$", chave))

    def is_email(chave):
        return bool(
            re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", chave)
        )

    def is_chave_aleatoria(chave):
        return bool(re.match(r"^[0-9A-Fa-f]{32}$", chave))

    if not (
        is_cpf_cnpj(chave)
        or is_celular(chave)
        or is_email(chave)
        or is_chave_aleatoria(chave)
    ):
        raise ValidationError(detail={"detail": "Chave PIX inválida."})
