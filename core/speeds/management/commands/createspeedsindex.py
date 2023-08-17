import time

from django.core.management.base import BaseCommand, CommandError

from core.meilisearch import client


class Command(BaseCommand):
    help = "Creates speeds index for the Meilisearch search engine"

    def handle(self, *args, **options):
        if not client.is_disabled() and client.is_healthy():
            try:
                client.get_index('speeds')
            except Exception as e:
                task = client.create_index(
                    uid='speeds',
                    # same as a Speed's model pk (UUID4)
                    options={
                        'primaryKey': 'id'
                    }
                )
                
                time.sleep(0.1)
                task = client.get_task(task.task_uid)
                start_time = time.time()
                check_interval = 0.5
                while time.time() - start_time < 4 and task.status != 'succeeded':
                    if time.time() - start_time > check_interval:
                        task = client.get_task(task.uid)
                        check_interval += 0.5
                
                if task.status != 'succeeded':
                    raise Exception("Meiliserch `create_index()` has timed out.")
                
                # move to core/speeds/management/commands/updatespeedsindex.py
                index = client.index('speeds')
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
                self.stdout.write(self.style.SUCCESS('Meilisearch `speeds` index was created!'))

        elif not client.is_disabled() and not client.is_healthy():
            raise Exception("Meilisearch is not healthy :(.")

        
