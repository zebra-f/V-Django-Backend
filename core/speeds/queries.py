from typing import Literal

from django.db.models import Q, OuterRef, Count
from django.db.models.functions import JSONObject, Random
from django.contrib.postgres.expressions import ArraySubquery

from .models import Speed, SpeedFeedback, SpeedBookmark
from core.users.models import User


class SpeedQueries:
    
    # anonymous users
    
    @staticmethod
    def get_anonymous_user_query():
        return Speed.objects\
                .filter(is_public=True)\
                .select_related('user')
        
    @staticmethod
    def get_random_list_query(limit: int):
        return Speed.objects\
                .filter(is_public=True, score__gt=0)\
                .order_by(Random())\
                .select_related('user')\
                [:limit]
    
    # authenticated users
    
    @staticmethod
    def get_user_speed_feedback_subquery(user: User):
        return SpeedFeedback.objects\
                .filter(speed=OuterRef('pk'), user=user)\
                .values(json=JSONObject(feedback_id="id", feedback_vote="vote"))

    @staticmethod
    def get_user_speed_bookmark_subquery(user: User):
        return SpeedBookmark.objects\
                .filter(speed=OuterRef('pk'), user=user)\
                .values(json=JSONObject(bookmark_id="id", bookmark_category="category"))

    @staticmethod
    def get_authenticated_user_query(user: User, mode: Literal['public_and_personal', 'personal']):
        if mode not in ('public_and_personal', 'personal'):
            raise ValueError('Invalid mode.')
        
        query_filter = None
        if mode == 'public_and_personal':
            query_filter = Q(is_public=True) | Q(user=user)
        elif mode == 'personal':
            query_filter = Q(user=user)
        
        return Speed.objects\
                .filter(query_filter)\
                .annotate(
                    user_speed_feedback=ArraySubquery(SpeedQueries.get_user_speed_feedback_subquery(user)),
                    user_speed_bookmark=ArraySubquery(SpeedQueries.get_user_speed_bookmark_subquery(user))
                )\
                .select_related('user')
    
    @staticmethod
    def get_admin_query(user: User):
        return Speed.objects\
                .annotate(
                    user_speed_feedback=ArraySubquery(SpeedQueries.get_user_speed_feedback_subquery(user)),
                    user_speed_bookmark=ArraySubquery(SpeedQueries.get_user_speed_bookmark_subquery(user))
                )\
                .select_related('user')

    # admin site

    @staticmethod
    def get_admin_site_query():
        return Speed.objects\
                .annotate(reports_count=Count('report'))\
                .order_by('-reports_count')\
                .prefetch_related('report')


class SpeedFeedbackQueries:

    @staticmethod
    def get_user_query(user: User):
        ''' 
        Retrieves user's feedbacks of user's speeds or user's feedbacks of public speeds 
        (which may have been changed to private after voting).
        '''
        return SpeedFeedback.objects\
                .filter(
                    (Q(user=user) & Q(speed__user=user)) | (Q(speed__is_public=True) & ~Q(speed__user=user) & Q(user=user))
                )\
                .select_related('user')\
                .select_related('speed')


class SpeedBookmarkQueries:

    @staticmethod
    def get_user_query(user: User):
        ''' 
        Retrieves user's bookmarks of user's speeds or user's bookmarks of public speeds 
        (which may have been changed to private after bookmarking).
        '''
        return SpeedBookmark.objects\
                .filter(
                    (Q(user=user) & Q(speed__user=user)) | (Q(speed__is_public=True) & ~Q(speed__user=user) & Q(user=user))
                )\
                .select_related('user')\
                .select_related('speed')