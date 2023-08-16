from django.core.management.base import BaseCommand, CommandError

from core.meilisearch import client


class Command(BaseCommand):
    help = "Creates speeds index for the Meilisearch search engine"

    def handle(self, *args, **options):
        if not client.is_disabled() and client.is_healthy():
            try:
                client.get_index('speeds')
            except Exception as e:
                index = client.create_index(
                    uid='speeds',
                    options={
                        'primaryKey': 'id'
                    }
                )
                index.update_settings({
                    'rankingRules': [
                        'name',
                        'description',
                        'tags',
                        ],
                    'searchableAttributes': [
                        'name',
                        'description',
                        'speed_type'
                        'tags',
                        ],
                    'displayedAttributes': [
                        'speed_id'
                        'name',
                        'description',
                        'speed_type',
                        'tags',
                        'username',
                        'updated_at',
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
                        'disableOnAttributes': ['tags', 'description']
                        },
                    'pagination': {
                        'maxTotalHits': 10
                        },
                    })
        elif not client.is_disabled() and not client.is_healthy():
            raise Exception("Meilisearch is not healthy :(.")

        self.stdout.write(self.style.SUCCESS('Hello from createspeedsindex command!'))
