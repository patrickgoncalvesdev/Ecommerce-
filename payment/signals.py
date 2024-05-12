from payment.models import WithDrawRequest, PaymentConfigTable
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=WithDrawRequest)
def create_a_new_withdraw_payment_integration_request(
    sender, instance: WithDrawRequest, created, **kwargs
):
    logger.warning(f"New withdraw request {instance} created")
    ## TODO quando tiver a conta da pagarme chamar a api de saque caso seja aprovado
    # if created:
    #     config = PaymentConfigTable.get_config()

    #     if config.withdraw_auto_approve:
    #         logger.warning(
    #             f"Auto approve is enabled, approving withdraw request {instance}"
    #         )
    #         if instance.value <= config.max_auto_withdraw_value:
    #             logger.warning(
    #                 f"Withdraw request {instance} is below the max auto approve value, approving"
    #             )
    #         else:
    #             logger.warning(
    #                 f"Withdraw request {instance} is above the max auto approve value, approving"
    #             )
