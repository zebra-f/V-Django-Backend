import logging

from .celery import app as celery_app


logger = logging.getLogger(__name__)

__all__ = ('celery_app',)