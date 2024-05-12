from django.apps import AppConfig
from django.utils import timezone
import threading


class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce"

    def ready(self) -> None:
        from . import signals
        
