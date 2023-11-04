from typing import Literal

from meilisearch import Client

from django.conf import settings
from django.db import transaction, models

from core.speeds.models import Speed
from . import logger


def run_if_not_disabled(method):
    def wrapper(self, *args, **kwargs):
        if not self.is_disabled():
            method(self, *args, **kwargs)

    return wrapper


class MeilisearchClient(Client):
    django_settings = settings

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.displayed_attributes_dict = {
            Speed.__name__.lower()
            + "s": [
                "id",
                "name",
                "description",
                "speed_type",
                "user",
                "tags",
                "kmph",
                "estimated",
                "score",
                "is_public",
            ]
        }
        self.index_models = {Speed.__name__.lower() + "s": Speed}

        for index_name, model in self.index_models.items():
            fields = [field.name for field in model._meta.get_fields()]
            # checks if all `displayed_attributes_dict[index_name]` are present in a model
            if not all(
                [
                    attr in fields
                    for attr in self.displayed_attributes_dict[index_name]
                ]
            ):
                logger.critical(
                    f"core.{__name__}; A field in the {model.__name__} model has been changed!"
                )
                raise Exception(
                    f"A field in the {model.__name__} model has been changed!"
                )

    def is_disabled(self) -> bool:
        return self.django_settings.MEILISEARCH["disabled"]

    def task_succeeded(self, task_info, timeout_in_ms: int = 5000) -> bool:
        task = self.wait_for_task(task_info.task_uid, timeout_in_ms)

        if task.status != "succeeded":
            return False
        return True

    @run_if_not_disabled
    def sync_document(
        self,
        index_name: Literal["speeds"],
        action: Literal["add", "update"],
        data: dict,
    ) -> None:
        with transaction.atomic():
            try:
                model: models.Model = self.index_models[index_name]
                data = {
                    key: val
                    for key, val in data.items()
                    if key in self.displayed_attributes_dict[index_name]
                }
                pk = data["id"]
                instance = model.objects.select_for_update().get(pk=pk)
            except Exception as e:
                logger.error(f"core.{__name__}; {str(e)}")
                return

            document: dict = data
            task_info = self.index(index_name).update_documents([document])

            if self.task_succeeded(task_info):
                if action == "add":
                    instance.mark_added_to_meilisearch()
                elif action == "update":
                    instance.mark_synced_in_meilisearch()
            else:
                logger.error(f"core.{__name__}; {pk} was not {action}ed!")


URL = settings.MEILISEARCH["URL"]
MASTER_KEY = settings.MEILISEARCH["MASTER_KEY"]

client = MeilisearchClient(url=URL, api_key=MASTER_KEY)
