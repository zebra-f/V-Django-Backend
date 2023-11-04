import time

from django.core.management.base import BaseCommand

from core.speeds.models import Speed
from core.meilisearch import client


class Command(BaseCommand):
    help = "Creates the 'speeds' index for the Meilisearch search engine if it doesn't exists yet."

    def handle(self, *args, **options):
        if not client.is_disabled():
            timeout = 100  # 100 microseconds
            while not client.is_healthy and timeout > 0:
                time.sleep(0.2)
                timeout -= 2

        if not client.is_disabled() and client.is_healthy():
            index_name = None
            for index, model in client.index_models.items():
                if model == Speed:
                    index_name = index
            try:
                client.get_index(index_name)
            except Exception as e:
                task_info = client.create_index(
                    uid=index_name,
                    # same as a Speed's model pk (UUID4)
                    options={"primaryKey": "id"},
                )

                if client.task_succeeded(task_info):
                    self.stdout.write(
                        self.style.SUCCESS(
                            "Meilisearch's `speeds` index was created!"
                        )
                    )
                else:
                    raise Exception(
                        "Meiliserch `create_index()` has timed out."
                    )
        elif not client.is_disabled() and not client.is_healthy():
            raise Exception("Meilisearch is not healthy :(.")
        else:
            raise Exception(
                "Meilisearch is currently disabled in this application. If you'd like to enable it, please configure the settings in your settings.py file."
            )
