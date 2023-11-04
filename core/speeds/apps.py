from django.apps import AppConfig


class SpeedsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.speeds"

    def ready(self) -> None:
        return super().ready()
