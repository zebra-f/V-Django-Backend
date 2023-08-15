from meilisearch import Client

from django.conf import settings


class MeilisearchClient(Client):

    def is_disabled(self) -> bool:
        return settings.MEILISEARCH['disabled']


URL = settings.MEILISEARCH['URL']
MASTER_KEY = settings.MEILISEARCH['MASTER_KEY']
client = MeilisearchClient(URL, MASTER_KEY)

# explicit index creation
def create_meilisearch_index(name: str, fields: list) -> None:
    index = client.create_index(name)
    index.update_attributes_for_faceting(fields)

if __name__ == '__main__':
    if not client.is_disabled() and client.is_healthy():
        try:
            client.get_index('speeds')
        except Exception as e:
            speed_index_config = {
                'name': 'speeds',
                'fields': ['id', 
                           'name', 
                           'description', 
                           'kmph', 
                           'estimated', 
                           'username', 
                           'updated_at', 
                           'sync_id'
                           ],
            }
            create_meilisearch_index(
                speed_index_config['name'], 
                speed_index_config['fields']
                )
    elif not client.is_disabled() and not client.is_healthy():
        raise Exception("Meilisearch is not healthy :(.")
