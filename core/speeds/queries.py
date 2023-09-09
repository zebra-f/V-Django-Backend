from django.db.models import Q, Subquery, Case, FilteredRelation, Value, IntegerField, When, Exists, OuterRef, Prefetch
from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedBookmark
from core.users.models import User
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models.functions import JSONObject

class SpeedViewSetQueries:

    @staticmethod
    def get_anonymous_user_query():
        return Speed.objects.filter(is_public=True).prefetch_related(
                'feedback_counter'
            ).annotate(
                user_speed_feedback_vote=Value(-3),
                user_speed_bookmark=Value(False)
            )

    @staticmethod
    def get_authenticated_user_query(user: User):
        test_subquery = SpeedFeedback.objects.filter(
                            speed=OuterRef('pk'), user=user
                        ).values(json=JSONObject(test_vote="vote", test_id="id"))
        return Speed.objects.filter(
                Q(is_public=True) | Q(user=user)
            ).prefetch_related(
                'feedback_counter'
            ).annotate(
                user_speed_feedback_vote=Subquery(
                    SpeedFeedback.objects.filter(
                        speed=OuterRef('pk'), user=user).values('vote')
                    ),
                user_speed_bookmark=Subquery(
                    SpeedBookmark.objects.filter(
                        speed=OuterRef('pk'), user=user).values('category')
                    ),
                test=ArraySubquery(test_subquery)
            )
    
    @staticmethod
    def get_authenticated_user_personal_query(user: User):
        """ A query to retrieve objects created by the authenticated user. """
        return Speed.objects.filter(
                user=user
            ).prefetch_related(
                'feedback_counter'
            ).annotate(
                user_speed_feedback_vote=Subquery(
                    SpeedFeedback.objects.filter(
                        speed=OuterRef('pk'), user=user).values('vote')
                    ),
                user_speed_bookmark=Subquery(
                    SpeedBookmark.objects.filter(
                        speed=OuterRef('pk'), user=user).values('category')
                    )
            )

    @staticmethod
    def get_admin_query(user: User):
        return Speed.objects.prefetch_related(
                'feedback_counter'
            ).annotate(
                user_speed_feedback_vote=Subquery(
                    SpeedFeedback.objects.filter(
                        speed=OuterRef('pk'), user=user).values('vote')
                    ),
                user_speed_bookmark=Subquery(
                    SpeedBookmark.objects.filter(
                        speed=OuterRef('pk'), user=user).values('category')
                    )
            )
    

class SpeedFeedbackQueries:

    @staticmethod
    def get_user_query(user: User):
        return SpeedFeedback.objects.filter(
            (Q(user=user) & Q(speed__user=user)) | (Q(speed__is_public=True) & ~Q(speed__user=user) & Q(user=user))
        )


class SpeedBookmarkQueries:

    @staticmethod
    def get_user_query(user: User):
        return SpeedBookmark.objects.filter(
                (Q(user=user) & Q(speed__user=user)) | (Q(speed__is_public=True) & ~Q(speed__user=user) & Q(user=user))
            )