from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly

from django.shortcuts import get_object_or_404
from django.db.models import Q, Subquery, Case, FilteredRelation, Value, IntegerField, When, Exists, OuterRef

from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedBookmark
from .permissions import UserIsAuthorized, ForbiddenAction
from .serializers import SpeedSerializer, SpeedFeedbackSerializer, SpeedFeedbackFrontendSerializer

from django.core.cache import cache
 

class SpeedViewSet(viewsets.ModelViewSet):
    queryset = Speed.objects.prefetch_related('feedback_counter')
    serializer_class = SpeedSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    object_level_actions = [
        'destroy',
        'update',
        'partial_update',
        'list_personal'
        ]
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve',):
            self.permission_classes = [AllowAny]
        if self.action in ('create',):
            self.permission_classes = [UserIsAuthorized]
        if self.action in self.object_level_actions:
            self.permission_classes = [UserIsAuthorized]
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ('list', 'retrieve',):
            if self.request.user.is_anonymous:
                return Speed.objects.filter(is_public=True).prefetch_related(
                    'feedback_counter'
                    ).annotate(user_speed_feedback=Value(-3))
            elif not self.request.user.is_admin:
                return Speed.objects.filter(
                        Q(is_public=True) | Q(user=self.request.user)
                    ).prefetch_related(
                        'feedback_counter'
                    ).annotate(
                        user_speed_feedback=Subquery(
                            SpeedFeedback.objects.filter(
                                speed=OuterRef('pk'), user=self.request.user).values('vote')
                            )
                    )
        if self.action in ('list_personal',):
            return Speed.objects.filter(
                    user=self.request.user
                ).prefetch_related(
                    'feedback_counter'
                ).annotate(
                    user_speed_feedback=Subquery(
                        SpeedFeedback.objects.filter(
                            speed=OuterRef('pk'), user=self.request.user).values('vote')
                        )
                )

        return super().get_queryset()
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response
    
    @action(methods=['get'], detail=False, url_path='list-personal')
    def list_personal(self, request, *args, **kwargs):
        ''' a queryset for this action is defined in the get_queryset() method '''
        return self.list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SpeedFeedbackViewSet(viewsets.ModelViewSet):
    queryset = SpeedFeedback.objects.all()
    serializer_class = SpeedFeedbackSerializer
    # User should always be authorized for any action in this ViewSet
    permission_classes = [UserIsAuthorized]
    object_level_actions = [
        'retrieve',
        'partial_update',
        ]
    forbidden_object_level_actions = [
        'update',
        'destroy',
    ]

    def get_permissions(self):
        if self.action in self.forbidden_object_level_actions:
            self.permission_classes = [ForbiddenAction]
        return super().get_permissions()
    
    def get_queryset(self):
        # return super().get_queryset()
        if self.request.user.is_admin or self.action in self.object_level_actions:
            return super().get_queryset()
        else:
            return SpeedFeedback.objects.filter(user=self.request.user)
        
    def get_serializer(self, *args, **kwargs):
        if self.action in ('create_or_partial_update',):
            return SpeedFeedbackFrontendSerializer
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['get', 'post', 'patch'], detail=False, url_path='create-or-partial-update')
    def create_or_partial_update(self, request):
        serializer = self.get_serializer()
        print('a')
        if request.method == 'POST':
            print('a')
            pass
        elif request.method == 'PATCH':
            print('b')
            pass
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

        


