import time

from django.core.management.base import BaseCommand, CommandError

from core.meilisearch import client
from core.speeds.models import Speed
from core.speeds import logger


class Command(BaseCommand):
    help = "Updates the 'speeds' index for the Meilisearch search engine if it already exists."

    def handle(self, *args, **options):
        if not client.is_disabled():
            timeout = 100  # 100 microseconds
            while not client.is_healthy and timeout > 0:
                time.sleep(0.2)
                timeout -= 2
        
        if not client.is_disabled() and client.is_healthy():
            index = None
            
            try:
                index = client.get_index('speeds')
            except Exception as e:
                raise e
            
            if not index:
                raise Exception('Something went wrong')
            
            displayed_attributes = [
                'id',
                'name',
                'description',
                'speed_type',
                'tags',
                'kmph',
                'estimated',
                'user',
                'updated_at',
                'score'
            ]
            fields = [field.name for field in Speed._meta.get_fields()]
            # checks if all `displayed_attributes` are present in the `Speed` model
            if not all([attr in fields for attr in displayed_attributes]):
                logger.critical("A field in the `Speed` model has been changed!")
                raise Exception("A field in the `Speed` model has been changed!")
            
            index.update_settings({
                'rankingRules': [
                    "words",
                    "typo",
                    "proximity",
                    "attribute",
                    "sort",
                    "exactness"
                    ],
                'searchableAttributes': [
                    'name',
                    'description',
                    'speed_type'
                    ],
                'displayedAttributes': [
                    'id',
                    'name',
                    'description',
                    'speed_type',
                    'tags',
                    'kmph',
                    'username',
                    'updated_at',
                    'score',
                    ],
                'sortableAttributes': [],
                'stopWords': [
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
                    "at"
                    ],
                'typoTolerance': {
                    'enabled': True,
                    'minWordSizeForTypos': {
                        'oneTypo': 6,
                        'twoTypos': 10
                        },
                    'disableOnAttributes': ['description', 'speed_type']
                    },
                'pagination': {
                    'maxTotalHits': 10
                    },
                })
            self.stdout.write(self.style.SUCCESS("Meilisearch's `speeds` index was updated!"))
        elif not client.is_disabled() and not client.is_healthy():
            raise Exception("Meilisearch is not healthy :(.")
        else:
            raise Exception(
                "Meilisearch is currently disabled in this application. If you'd like to enable it, please configure the settings in your settings.py file."
                )

        
