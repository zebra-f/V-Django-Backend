import time

from django.core.management.base import BaseCommand

from core.meilisearch import client
from core.speeds.models import Speed


class Command(BaseCommand):
    help = "Updates the 'speeds' index for the Meilisearch search engine if it already exists."

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
                index = client.get_index(index_name)
            except Exception as e:
                raise e

            if not index:
                raise Exception("Something went wrong")

            index.update_settings(
                {
                    "rankingRules": [
                        "words",
                        "typo",
                        "proximity",
                        "attribute",
                        "sort",
                        "exactness",
                    ],
                    "searchableAttributes": [
                        "name",
                        "description",
                        "speed_type",
                    ],
                    "displayedAttributes": [
                        *client.displayed_attributes_dict[index_name]
                    ],
                    "sortableAttributes": [],
                    "stopWords": [
                        "the",
                        "a",
                        "an",
                        "is",
                        "on",
                        "in",
                        "of",
                        "and",
                        "to",
                        "with",
                        "for",
                        "can",
                        "be",
                        "at",
                    ],
                    "typoTolerance": {
                        "enabled": True,
                        "minWordSizeForTypos": {"oneTypo": 6, "twoTypos": 10},
                        "disableOnAttributes": ["description", "speed_type"],
                    },
                    "pagination": {"maxTotalHits": 10},
                }
            )
            self.stdout.write(
                self.style.SUCCESS("Meilisearch's `speeds` index was updated!")
            )
        elif not client.is_disabled() and not client.is_healthy():
            raise Exception("Meilisearch is not healthy :(.")
        else:
            raise Exception(
                "Meilisearch is currently disabled in this application. If you'd like to enable it, please configure the settings in your settings.py file."
            )
