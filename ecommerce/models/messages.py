from django.db import models
from django.template import Engine, Context


class MessagesTemplate(models.Model):
    register_message = models.TextField(
        default="""Clique no link abaixo para ativar a conta
    https://jb.ecommerce/register/activated?code={{user_code}} ou utilize o código {{user_code}}""",
        verbose_name="Mensagem registro (html) contexto(payload,user,status)",
    )

    update_message = models.TextField(
        default="""Clique no link abaixo para atualizar o perfil
    https://jb.ecommerce/register/activated?code={{user_code}} ou utilize o código {{user_code}}""",
        verbose_name="Mensagem atualização (html) contexto(payload,user,status)",
    )
    
    recovery_message = models.TextField(
        default="""Clique no link abaixo para recuperar a senha
    https://jb.ecommerce/register/activated?code={{user_code}} ou utilize o código {{user_code}}""",
        verbose_name="Mensagem atualização (html) contexto(payload,user,status)",
    )
    
    sms_register_message = models.CharField(
        default="DATAGAMING - Utilize o seguinte código para ativar sua conta: {{user_code}}",
        max_length=255,
        verbose_name="Mensagem registro (sms)",
    )
    sms_update_message = models.CharField(
        default="DATAGAMING - Utilize o seguinte código para atualizar seu perfil: {{user_code}}",
        max_length=255,
        verbose_name="Mensagem atualização (sms)",
    )
    
    sms_recovery_message = models.CharField(
        default="DATAGAMING - Utilize o seguinte código para recuperar a senha: {{user_code}}",
        max_length=255,
        verbose_name="Mensagem atualização (sms)",
    )

    def __mount_message_template(self, template: str, context_data: dict):
        context = Context(context_data)
        engine = Engine.get_default()
        engine_template = engine.from_string(template)
        return engine_template.render(context)

    def register_message_template(self, context_data: dict):
        return self.__mount_message_template(self.register_message, context_data)

    def update_message_template(self, context_data: dict):
        return self.__mount_message_template(self.update_message, context_data)
    
    def update_recovery_template(self, context_data: dict):
        return self.__mount_message_template(self.recovery_message, context_data)

    def sms_register_message_template(self, context_data: dict) -> str:
        return self.__mount_message_template(self.sms_register_message, context_data)

    def sms_update_message_template(self, context_data: dict) -> str:
        return self.__mount_message_template(self.sms_update_message, context_data)
    
    def sms_recovery_message_template(self, context_data: dict) -> str:
        return self.__mount_message_template(self.sms_recovery_message, context_data)


# Path: ecommerce/models/messages.py
