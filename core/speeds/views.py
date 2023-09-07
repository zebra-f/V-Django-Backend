from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer

from django.shortcuts import get_object_or_404
from django.db.models import Value
from django.core.cache import cache
 

from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedBookmark
from .permissions import UserIsAuthorized, ForbiddenAction
from .serializers import SpeedSerializer, SpeedFeedbackSerializer, SpeedFeedbackFrontendSerializer, SpeedBookmarkSerializer
from .renderers import CustomBrowsableAPIRenderer
from .queries import SpeedViewSetQueries, SpeedBookmarkQueries

class SpeedViewSet(viewsets.ModelViewSet):
    renderer_classes = [CustomBrowsableAPIRenderer, JSONRenderer]
    queryset = Speed.objects.prefetch_related('feedback_counter').annotate(user_speed_feedback=Value(-3))
    serializer_class = SpeedSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    object_level_actions = [
        'destroy',
        'update',
        'partial_update',
        ]
    object_level_actions_to_restrict = [
            *object_level_actions
        ]
    actions_to_restrict = [
        'list_personal',
        'create'
        ]
    
    def get_permissions(self):
        # a queryset should return only a non private data
        if self.action in ('list', 'retrieve',):
            self.permission_classes = [AllowAny]
        if (
            self.action in self.object_level_actions_to_restrict or 
            self.action in self.actions_to_restrict
        ):
            self.permission_classes = [UserIsAuthorized]

        return super().get_permissions()

    def get_queryset(self):
        if self.action in ('list', 'retrieve',):
            # an anonymous user
            if self.request.user.is_anonymous:
                return SpeedViewSetQueries.get_anonymous_user_query()
            # an user
            elif not self.request.user.is_admin:
                return SpeedViewSetQueries.get_authenticated_user_query(self.request.user)
            # an admin
            else:
                return SpeedViewSetQueries.get_admin_query(self.request.user)
        if self.action in ('list_personal',):
            return SpeedViewSetQueries.get_authenticated_user_personal_query(self.request.user)

        return super().get_queryset()
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response
    
    @action(methods=['get'], detail=False, url_path='list-personal')
    def list_personal(self, request, *args, **kwargs):
        ''' a queryset for this action is defined in the `get_queryset` method '''
        return self.list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SpeedFeedbackViewSet(viewsets.ModelViewSet):
    queryset = SpeedFeedback.objects.all()
    serializer_class = SpeedFeedbackSerializer
    # a user should always be authorized for any action in this ViewSet
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
        # protected by the permission_classes
        if self.request.user.is_admin or self.action in self.object_level_actions:
            return super().get_queryset()
        # for the list view
        else:
            return SpeedFeedback.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ('frontend_partial_update',):
            return SpeedFeedbackFrontendSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['patch'], detail=False, url_path='frontend-partial-update')
    def frontend_partial_update(self, request):
        ''' used by a frontend client, with no access to a SpeedFeedback primary key '''
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            speed_feedback = get_object_or_404(
                SpeedFeedback,
                speed=serializer.data['speed'], 
                user=self.request.user
                )
            speed_feedback.vote = serializer.data['vote']
            speed_feedback.save(update_fields=['vote'])
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

class SpeedBookmarkViewSet(viewsets.ModelViewSet):
    queryset = SpeedBookmark.objects.all()
    serializer_class = SpeedBookmarkSerializer
    # a user should always be authorized for any action in this ViewSet
    permission_classes = [UserIsAuthorized]
    object_level_actions = [
        'retrieve',
        'partial_update',
        ]
    forbidden_object_level_actions = [
        'update',
        ]
    
    def get_permissions(self):
        if self.action in self.forbidden_object_level_actions:
            self.permission_classes = [ForbiddenAction]
        return super().get_permissions()
    
    def get_queryset(self):
        # protected by the permission_classes
        if self.request.user.is_admin or self.action in self.object_level_actions:
            return super().get_queryset()
        # for the list view
        else:
            return SpeedBookmarkQueries.get_user_query(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        


