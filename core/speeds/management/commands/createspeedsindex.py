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
                check_interval = 0.2
                while time.time() - start_time < 4 and task.status != 'succeeded':
                    if time.time() - start_time > check_interval:
                        # refreshes task status
                        task = client.get_task(task.uid)
                        check_interval += 0.2
                
                if task.status != 'succeeded':
                    raise Exception("Meiliserch `create_index()` has timed out.")
                
                self.stdout.write(self.style.SUCCESS("Meilisearch's `speeds` index was created!"))
        elif not client.is_disabled() and not client.is_healthy():
            raise Exception("Meilisearch is not healthy :(.")
        else:
            raise Exception(
                "Meilisearch is currently disabled in this application. If you'd like to enable it, please configure the settings in your settings.py file."
                )

        
