import pickle
from random import sample
from collections import OrderedDict

from django.core.cache import cache

from .queries import SpeedQueries
from .serializers import BasicSpeedSerializer
from . import logger


r = cache.client.get_client()

def cache_random_speeds(k: int=1200) -> None:
    '''
    This function is responsible for generating and storing random `Speed` objects in the Redis cache,
    along with caching the `upper_limit` (length value) of the generated list.
    Random speed objects are cached as key-value pairs, 
    where keys (integers) are within the closed range from 0 to (`upper_limit` - 1).
    '''
    random_speeds_list = BasicSpeedSerializer(
        SpeedQueries.get_random_list_query(k), 
        many=True,
    )
    mapping = {}
    for i, speed in enumerate(random_speeds_list.data):
        # <class 'collections.OrderedDict'>
        pickled = pickle.dumps(speed)
        mapping[str(i)] = pickled
    
    # `mapping` keys range from 0 to (`upper_limit` - 1) inclusive
    upper_limit = len(mapping)
    
    r.hset('random_speeds_hash', mapping=mapping)
    #                               s  m  h    s  m
    r.expire('random_speeds_hash', (60*60*12)+(60*20))
    r.set('random_speeds_hash_upper_limit', upper_limit)
    r.expire('random_speeds_hash_upper_limit', (60*60*12)+(60*20))

def get_random_speeds(k: int=10) -> OrderedDict:
    '''
    This function is responsible for retrieving `k` random `Speed` objects from the Redis cache.
    It returns a 'ready-to-serve' data for a DRF view's response.
    '''
    upper_limit = int(r.get('random_speeds_hash_upper_limit'))
    k = k if upper_limit >= k else upper_limit
    
    random_keys = sample(range(upper_limit), k)
    random_speeds_list = []
    flag = False
    for key in random_keys:
        # <class 'collections.OrderedDict'>
        speed = r.hget(key=str(key), name='random_speeds_hash')
        if speed != None:
            random_speeds_list.append(pickle.loads(speed))
        else:
            flag = True
    
    if flag:
        logger.debug(
            f"speeds(app); `{get_random_speeds.__name__}` is not functioning correctly. " + \
            f"Length of random_speeds_list == {len(random_speeds_list)}, upper_limit == {upper_limit}."
            )

    random_speeds = OrderedDict()
    random_speeds['count'] = len(random_speeds_list)
    random_speeds['next'] = None
    random_speeds['previous'] = None
    random_speeds['results'] = random_speeds_list

    return random_speeds



