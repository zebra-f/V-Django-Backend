"""
If Meilisearch is not disabled in the settings, run this command in a terminal: 
    
    $ python3 manage.py createspeedsindex

"""
import time

from meilisearch import Client

from django.conf import settings


class MeilisearchClient(Client):

    def is_disabled(self) -> bool:
        return settings.MEILISEARCH['disabled']
    
    def task_succeeded(self, task_info, timeout: int=4) -> bool:
        time.sleep(0.02)
        task = self.get_task(task_info.task_uid)
        timestamp = time.time()
        while time.time() - timestamp < timeout and task.status != 'succeeded':
            time.sleep(0.02)
            # refreshes task status
            task = self.get_task(task_info.task_uid)
                
        if task.status != 'succeeded':
            return False  
        return True


URL = settings.MEILISEARCH['URL']
MASTER_KEY = settings.MEILISEARCH['MASTER_KEY']

client = MeilisearchClient(url=URL, api_key=MASTER_KEY)