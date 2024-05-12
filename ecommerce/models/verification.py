from django.db import models
from ecommerce.utils.consts import VerificationType
from ecommerce.utils.verifications import get_expiration_time, get_datetime_now
from django.utils.crypto import get_random_string
from django.utils import timezone
from ecommerce.models.user import UserAPI


def generate_token():
    token = get_random_string(length=6)
    if Verification.objects.filter(token=token).exists():
        return generate_token()
    return token

class Verification(models.Model):
    token = models.CharField(default=generate_token, unique=True, max_length=6)
    type = models.CharField(max_length=20, choices=VerificationType.choices)
    actived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiration_time)
    resend_expires_at = models.DateTimeField(default=get_datetime_now)
    user = models.ForeignKey(UserAPI, on_delete=models.CASCADE)
    data = models.JSONField()
    
    class Meta:
        verbose_name = "Verificação"
        verbose_name_plural = "Verificações"
         
    @staticmethod
    def _desactive_others_verifications(user, type):
        Verification.objects.filter(user=user, type=type, expires_at__gte=timezone.now(), actived=False).update(expires_at=timezone.now() - timezone.timedelta(minutes=1))
        
    @staticmethod
    def _check_verification(user, type):
        return Verification.objects.filter(user=user, type=type, expires_at__gte=timezone.now(), actived=False).exists()
    