import time

from django.core.management.base import BaseCommand, CommandError

from core.meilisearch import client


class Command(BaseCommand):
    help = "Creates speeds index for the Meilisearch search engine"

    def handle(self, *args, **options):
        if not client.is_disabled() and client.is_healthy():
            index = None
            
            try:
                index = client.get_index('speeds')
            except Exception as e:
                raise e
            
            if not index:
                raise Exception('Something went wrong')
            
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

        
