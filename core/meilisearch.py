"""
If Meilisearch is not disabled in the settings, run this command in a terminal: 
    
    $ python3 manage.py createspeedsindex

"""
from meilisearch import Client

from django.conf import settings


class MeilisearchClient(Client):

    def is_disabled(self) -> bool:
        return settings.MEILISEARCH['disabled']


URL = settings.MEILISEARCH['URL']
MASTER_KEY = settings.MEILISEARCH['MASTER_KEY']

client = MeilisearchClient(url=URL, api_key=MASTER_KEY)
