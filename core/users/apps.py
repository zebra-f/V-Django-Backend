from django.apps import AppConfig
from django.db.models.signals import pre_save

from .signals import handle_user_ban


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.users"

    def ready(self):
        from .models import User

        pre_save.connect(receiver=handle_user_ban, sender=User)

        return super().ready()
