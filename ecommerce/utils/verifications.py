from django.utils import timezone
from django.conf import settings


def get_expiration_time():
    return timezone.now() + timezone.timedelta(minutes=settings.EXPIRATION_TIME)

def get_datetime_now():
    return timezone.now()
