from celery.schedules import crontab

from core.celery import app
from .services import cache_random_speeds
from . import logger


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    try:
        # cache random `Speed` objects to ensure their availability for the client
        # before the first periodic task is called, which refreshes the cache every x hours.
        cache_random_speeds()
    except Exception as e:
        logger.error(f"speeds(app); {setup_periodic_tasks.__name__} initial caching failed, {str(e)}")
    
    sender.add_periodic_task(
        crontab(
            minute=0, hour='*/12'
        ), cache_random_speeds_task.s(), name='cache random speeds'
    )

@app.task  # doesn't work with @app.shared_task
def cache_random_speeds_task(**kwargs):
    '''
    Periodic task.
    '''
    try:
        cache_random_speeds()
    except Exception as e:
        logger.error(f"speeds(app); {cache_random_speeds_task.__name__} is not working properly, {str(e)}")