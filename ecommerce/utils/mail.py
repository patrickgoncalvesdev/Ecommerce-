from ecommerce.models.messages import MessagesTemplate


def get_register_message(email: str, token: str) -> (str, str):
    email_template = MessagesTemplate.objects.first()
    body = email_template.register_message_template(
        {"user_code": token, "email": email}
    )
    title = "Verificação de cadastro"
    return title, body


def get_sms_register_message(token: str) -> str:
    email_template = MessagesTemplate.objects.first()
    body = email_template.sms_register_message_template({"user_code": token})
    return body


def get_sms_update_message(token: str) -> str:
    email_template = MessagesTemplate.objects.first()
    body = email_template.sms_update_message_template({"user_code": token})
    return body

def get_sms_recovery_message(token: str) -> str:
    email_template = MessagesTemplate.objects.first()
    body = email_template.sms_recovery_message_template({"user_code": token})
    return body


def get_update_perfil_message(email: str, token: str) -> (str, str):
    title = "Verificação de atualização de perfil"
    body = f"""
        Olá {email}, seu código de verificação é {token},
        clique no link para confirmar sua atualização de perfil
    """
    return title, body
