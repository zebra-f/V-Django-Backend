import time

from celery.schedules import crontab

from django.contrib.auth import get_user_model

from core.celery import app
from core.meilisearch import client as ms_client
from .services import cache_random_speeds
from .queries import SpeedQueries
from . import logger


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    cache_flag = False
    try:
        # cache random `Speed` objects to ensure their availability for the client
        # before the first periodic task is called, which refreshes the cache every x hours.
        cache_random_speeds()
        cache_flag = True
    except Exception as e:
        logger.error(f"speeds(app); {setup_periodic_tasks.__name__} initial caching failed, {str(e)}")
    
    if cache_flag:
        sender.add_periodic_task(
            crontab(
                minute=0, hour='*/12'
            ), cache_random_speeds_task.s(), name='cache random speeds'
        )
    
    if not ms_client.is_disabled():
        sender.add_periodic_task(
            crontab(
                minute=0, hour='*/4'
            ), delete_meilisearch_deleted_user_data.s(), name='delete meilisearch deleted user data'
        )

@app.task  # doesn't work with @app.shared_task
def cache_random_speeds_task(**kwargs):
    '''
    Periodic task.
    '''
    try:
        cache_random_speeds()
    except Exception as e:
        logger.error(f"speeds(app).tasks; {cache_random_speeds_task.__name__} is not working properly, {str(e)}")

@app.task
def delete_meilisearch_deleted_user_data(**kwargs):
    user = get_user_model().objects.get(username="deleted")
    qs = SpeedQueries.get_deleted_user_query(
        user=user
    )
    
    timestamp = time.time()
    
    for speed in qs:
        try:
            task_info = ms_client.index('speeds').delete_document(speed.id)
            if ms_client.task_succeeded(task_info, 1):
                try:
                    speed.delete()
                except:
                    raise Exception(f'the `delete()` for {speed.id} has failed')
            else:
                logger.error(f'speeds(app).tasks; the `delete_document()` for {speed.id} has not succeeded.')
        except Exception as e:
            logger.error(f'speeds(app).tasks; {str(e)}.')
    
    logger.info(
        f'speeds(app).tasks; the `delete_meilisearch_deleted_user_data` perdiodic task has finished in {time.time() - timestamp} seconds.'
        )