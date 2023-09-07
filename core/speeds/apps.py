from django.apps import AppConfig
from django.db.models.signals import post_save


class SpeedsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.speeds'

    def ready(self) -> None:
        from .models import Speed
        from . import signals
        post_save.connect(signals.speed_post_save_handler, sender=Speed)
        return super().ready()
