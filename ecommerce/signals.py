from django.db.models.signals import post_save
from django.dispatch import receiver
from ecommerce.consumers import AMQPProducing
from ecommerce.models.client import Client
from ecommerce.models.affiliate import Affiliate
from ecommerce.models.lottery_draw import LotteryDraw
from ecommerce.models.verification import Verification
from ecommerce.models.money_moviment import MoneyMoviment
from ecommerce.utils.consts import VerificationType
from ecommerce.models.wallet import Wallet
from ecommerce.models.lottery import Lottery
from django.conf import settings
from ecommerce.models.pule import Pule
from ecommerce.models.quotation import Quotation
from ecommerce.models.bet import Bet
from ecommerce.models.config import Config
from ecommerce.models.first_deposit import FirstDeposit
from ecommerce.models.affiliate_config import AffiliateConfig
from ecommerce.models.affiliate_quotation import AffiliateQuotation
from ecommerce.utils.mail import (
    get_register_message,
    get_sms_register_message,
    get_sms_update_message,
    get_sms_recovery_message,
    get_update_perfil_message,
)
import threading
from django.utils import timezone
from ecommerce.utils.wallet import truncate
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Config)
def create_config(sender, instance, created, **kwargs):
    if created:
        instance.desactive_others()


@receiver(post_save, sender=FirstDeposit)
def create_first_deposit(sender, instance, created, **kwargs):
    if created:
        instance.desactive_others()

@receiver(post_save, sender=AffiliateConfig)
def create_affiliate_config(sender, instance, created, **kwargs):
    if created:
        instance.desactive_others()

@receiver(post_save, sender=Bet)
def create_bet(sender, instance, created, **kwargs):
    if created:
        if instance.pule.seller:
            seller_wallet = Wallet.objects.select_for_update().get(user=instance.pule.seller)
            quotation = instance.pule.seller.affiliate_quotations.get(quotation=instance.pule.user.quotation)
            MoneyMoviment.new_commission_transaction(
                value=truncate(instance.bet_value * quotation.percent / 100),
                wallet=seller_wallet,
                quotation=instance.pule.user.quotation,
                bet=instance,
            )

@receiver(post_save, sender=Affiliate)
def create_affiliate_verification(sender, instance, created, **kwargs):
    if created:
        logger.error(f"Affiliate created: {instance}")
        instance.set_password(instance.password)
        instance.is_active = True
        instance.wallet = Wallet.objects.create()
        config = Config.objects.last().affiliate
        instance.quotation = config.quotation
        instance.save()
        AffiliateQuotation.objects.create(
            affiliate=instance, quotation=config.quotation, percent=config.percent
        )

@receiver(post_save, sender=Client)
def create_client_verification(sender, instance, created, **kwargs):
    if created:
        instance.set_password(instance.password)
        instance.wallet = Wallet.objects.create()
        instance.save()
        Verification._desactive_others_verifications(
            instance, VerificationType.REGISTER
        )
        Verification.objects.create(
            user=instance, type=VerificationType.REGISTER, data={"is_active": True}
        )


@receiver(post_save, sender=Verification)
def create_verification(sender, instance, created, **kwargs):
    if created:
        if instance.type == VerificationType.REGISTER:
            title, text = get_register_message(instance.user.email, instance.token)
            sms_messagee = get_sms_register_message(instance.token)
        elif instance.type == VerificationType.UPDATE_PERFIL:
            title, text = get_update_perfil_message(instance.user.email, instance.token)
            sms_messagee = get_sms_update_message(instance.token)
        else:
            sms_messagee = get_sms_recovery_message(instance.token)
        """settings.MAIL_REPOSITORY.execute_async(
            to=instance.user.email,
            subject=title,
            body=text,
        )"""
        settings.SMS_REPOSITORY.execute_async(
            message=sms_messagee,
            number=instance.user.phone,
        )


@receiver(post_save, sender=LotteryDraw)
def create_a_job_to_lottery_draw(sender, instance: LotteryDraw, created, **kwargs):
    if created:
        til_cron_date = (instance.draw_trigger_date - timezone.now()).total_seconds()
        if til_cron_date > 0:
            draw_date = timezone.localtime(instance.date).strftime("%Y-%m-%d %H:%M:%S")
            logger.error(
                f"Time to cron: {til_cron_date} seconds or {(til_cron_date/60)/60} hours"
            )
            logger.error(f"Draw date: {draw_date}")
            logger.error(10 * "-")
            threading.Timer(
                til_cron_date,
                AMQPProducing.send_message,
                args=(
                    "jb_trigger",
                    {
                        "lotery_key": instance.lottery.lotery_key,
                        "target_lotery_datetime": draw_date,
                        "draw_id": instance.id,
                    },
                ),
            ).start()
    else:
        if not LotteryDraw.objects.filter(
            lottery=instance.lottery,
            is_active=True,
            date__gte=timezone.localtime(timezone.now()),
        ).exists():
            instance.lottery.create_lottery_draw_by_each_day_of_week_and_hour()


@receiver(post_save, sender=Lottery)
def create_a_job_to_lottery(sender, instance: Lottery, created, **kwargs):
    if created:
        instance.create_lottery_draw_by_each_day_of_week_and_hour()

