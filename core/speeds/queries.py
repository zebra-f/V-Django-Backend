from typing import Literal

from django.db.models import Q, Subquery, Case, FilteredRelation, Value, IntegerField, When, Exists, OuterRef, Prefetch
from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedBookmark
from core.users.models import User
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models.functions import JSONObject

class SpeedViewSetQueries:

    @staticmethod
    def get_anonymous_user_query():
        return Speed.objects\
                .filter(is_public=True)\
                .prefetch_related('feedback_counter')

    @staticmethod
    def get_authenticated_user_query(user: User, mode: Literal['public_and_personal', 'personal']):
        if mode not in ('public_and_personal', 'personal'):
            raise ValueError('Invalid mode.')
        
        query_filter = None
        if mode == 'public_and_personal':
            query_filter = Q(is_public=True) | Q(user=user)
        elif mode == 'personal':
            query_filter = Q(user=user)

        user_speed_feedback = SpeedFeedback.objects\
                .filter(speed=OuterRef('pk'), user=user)\
                .values(json=JSONObject(feedback_id="id", feedback_vote="vote"))
        user_speed_bookmark = SpeedBookmark.objects\
                .filter(speed=OuterRef('pk'), user=user)\
                .values(json=JSONObject(bookmark_id="id", bookmark_category="category"))
        
        return Speed.objects\
                .filter(query_filter)\
                .prefetch_related('feedback_counter')\
                .annotate(
                    user_speed_feedback=ArraySubquery(user_speed_feedback),
                    user_speed_bookmark=ArraySubquery(user_speed_bookmark)
                )
    
    @staticmethod
    def get_admin_query(user: User):
        user_speed_feedback = SpeedFeedback.objects\
                .filter(speed=OuterRef('pk'), user=user)\
                .values(json=JSONObject(feedback_id="id", feedback_vote="vote"))
        user_speed_bookmark = SpeedBookmark.objects\
                .filter(speed=OuterRef('pk'), user=user)\
                .values(json=JSONObject(bookmark_id="id", bookmark_category="category"))
        
        return Speed.objects\
                .prefetch_related('feedback_counter')\
                .annotate(
                    user_speed_feedback=ArraySubquery(user_speed_feedback),
                    user_speed_bookmark=ArraySubquery(user_speed_bookmark)
                )


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
                )


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
                )