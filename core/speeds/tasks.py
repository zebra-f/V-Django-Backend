import time
from typing import Literal

from celery.schedules import crontab
from celery import shared_task

from django.contrib.auth import get_user_model

from core.celery import app
from core.meilisearch import client as ms_client
from .queries import SpeedQueries
from .services import cache_random_speeds
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
        logger.error(f"core.speeds.{__name__}; {setup_periodic_tasks.__name__} initial caching failed, {str(e)}")
    
    if cache_flag:
        sender.add_periodic_task(
            crontab(
                minute='*/1'  # dev
                # minute=0, hour='*/12'  # prod
            ), cache_random_speeds_task.s(), name='cache random speeds'
        )
    
    if not ms_client.is_disabled():
        sender.add_periodic_task(
            crontab(
                minute='*/1'  # dev
                # minute=0, hour='*/4'  # prod
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
        logger.error(f"core.speeds.{__name__}; {cache_random_speeds_task.__name__} is not working properly, {str(e)}")

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
            if ms_client.task_succeeded(task_info):
                try:
                    speed.delete()
                except:
                    raise Exception(f'the `delete()` for {speed.id} has failed')
            else:
                print('2\n\n\n2\n\n\n', speed.id, '\n\n\n22222\n\n')
                logger.error(f'core.speeds.{__name__}; the `delete_document()` for {speed.id} has not succeeded.')
        except Exception as e:
            print('3\n\n\n3\n\n\n', speed.id, '\n\n\n333\n\n')
            logger.error(f'core.speeds.{__name__}; {str(e)}.')
    
    logger.info(
        f'core.speeds.{__name__}; the `delete_meilisearch_deleted_user_data` perdiodic task has finished in {time.time() - timestamp} seconds.'
        )

@shared_task
def sync_or_add_document_to_meiliserach(
        index: Literal['speeds'], 
        action: Literal['add', 'update'], 
        data: dict,
    ):
    ms_client.sync_document(index, action, data)