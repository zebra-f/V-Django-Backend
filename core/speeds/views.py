from rest_framework import viewsets, response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound

from django_filters.rest_framework import DjangoFilterBackend
 
from .models import (
    Speed, 
    SpeedFeedback, 
    SpeedBookmark, 
    SpeedReport
)
from .permissions import (
    UserIsAuthorized, 
    SpeedFeedbackPermissions, 
    SpeedBookmarkPermissions
)
from .serializers import (
    BaseHyperlinkedSpeedSerializer, 
    SpeedHyperlinkedSerializer, 
    SpeedFeedbackSerializer, 
    SpeedBookmarkSerializer, 
    SpeedReportSerializer
)
from core.common.renderers import CustomBrowsableAPIRenderer
from .queries import (
    SpeedQueries, 
    SpeedFeedbackQueries, 
    SpeedBookmarkQueries
)
from .filters import (
    SpeedFilter, 
    SpeedFeedbackFilter, 
    SpeedBookmarkFilter
)
from .services import get_random_speeds


class SpeedViewSet(viewsets.ModelViewSet):
    renderer_classes = [CustomBrowsableAPIRenderer, JSONRenderer]
    
    queryset = Speed.objects.filter(is_public=True)
    serializer_class = SpeedHyperlinkedSerializer
    
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = SpeedFilter
    
    object_level_actions = ['destroy', 'update', 'partial_update',]
    object_level_actions_to_restrict = [*object_level_actions]
    actions_to_restrict = ['personal_list', 'create']
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve',):
            self.permission_classes = [AllowAny]
        if (
            self.action in self.object_level_actions_to_restrict or 
            self.action in self.actions_to_restrict
        ):
            self.permission_classes = [UserIsAuthorized]

        return super().get_permissions()

    def get_queryset(self):
        if self.action in ('personal_list',) and not self.request.user.is_anonymous:
            return SpeedQueries.get_authenticated_user_query(self.request.user, 'personal')
        
        if self.request.user.is_anonymous:
            return SpeedQueries.get_anonymous_user_query()
        # an user
        elif not self.request.user.is_admin:
            return SpeedQueries.get_authenticated_user_query(self.request.user, 'public_and_personal')
        # an admin
        else:
            return SpeedQueries.get_admin_query(self.request.user)
        
    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return BaseHyperlinkedSpeedSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(methods=['get'], detail=False, url_path='personal-list')
    def personal_list(self, request, *args, **kwargs):
        '''
        In this context, 'personal list' refers to all the `Speed` data, including both public and private entries, 
        that have been added exclusively by the authenticated user.
        A queryset for this action is defined in the `get_queryset` method.
        A permission for this action is defined in the `get_permissions`.
        '''
        return self.list(request, *args, **kwargs)
    
    @action(methods=['get'], detail=False, url_path='random-list')
    def random_list(self, request, *args, **kwargs):
        '''
        An endpoint that retrieves a collection of random public Speed objects 
        stored in the Redis cache. 
        '''
        random_speeds_ord_dict = get_random_speeds()
        if random_speeds_ord_dict['count'] > 0:
            return response.Response(data=random_speeds_ord_dict, status=200)
        else:
            data = {
                "message": "Data not available. Please try again later."
                }
            return response.Response(data=data, status=404)


class SpeedFeedbackViewSet(viewsets.ModelViewSet):
    '''
    A user should always be authorized for any action in this ViewSet.
    '''
    queryset = SpeedFeedback.objects.all()
    serializer_class = SpeedFeedbackSerializer
    permission_classes = [UserIsAuthorized]

    filter_backends = [DjangoFilterBackend]
    filterset_class = SpeedFeedbackFilter
    
    not_allowed_http_method_names = ['put', 'delete']
    http_method_names = []
    for method_name in viewsets.ModelViewSet.http_method_names:
        if method_name not in not_allowed_http_method_names:
            http_method_names.append(method_name)

    object_level_actions = ['retrieve', 'partial_update',]
    forbidden_object_level_actions = ['update', 'destroy',]

    def get_permissions(self):
        if self.action in self.object_level_actions:
            self.permission_classes = [SpeedFeedbackPermissions]
        return super().get_permissions()

    def get_queryset(self):
        # secured by the permission_classes
        if self.request.user.is_admin or self.action in self.object_level_actions:
            return super().get_queryset()
        else:
            return SpeedFeedbackQueries.get_user_query(self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    

class SpeedBookmarkViewSet(viewsets.ModelViewSet):
    '''
    A user should always be authorized for any action in this ViewSet.
    '''
    queryset = SpeedBookmark.objects.all()
    serializer_class = SpeedBookmarkSerializer
    permission_classes = [UserIsAuthorized]

    filter_backends = [DjangoFilterBackend]
    filterset_class = SpeedBookmarkFilter
    
    not_allowed_http_method_names = ['put']
    http_method_names = []
    for method_name in viewsets.ModelViewSet.http_method_names:
        if method_name not in not_allowed_http_method_names:
            http_method_names.append(method_name)

    object_level_actions = ['destroy', 'retrieve', 'partial_update']
    forbidden_object_level_actions = ['update',]

    def get_permissions(self):
        if self.action in self.object_level_actions:
            self.permission_classes = [SpeedBookmarkPermissions]
        return super().get_permissions()
    
    def get_queryset(self):
        # secured by the permission_classes
        if self.request.user.is_admin or self.action in self.object_level_actions:
            return super().get_queryset()
        else:
            return SpeedBookmarkQueries.get_user_query(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SpeedReportViewSet(viewsets.ModelViewSet):
    '''
    A user should always be authorized for any action in this ViewSet.
    '''
    queryset = SpeedReport.objects.all()
    serializer_class = SpeedReportSerializer
    permission_classes = [UserIsAuthorized]

    def get_queryset(self):
        if self.request.user.is_admin:
            return super().get_queryset()
        return SpeedReport.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        if self.request.user.is_admin:
            return super().retrieve(request, *args, **kwargs)
        raise NotFound()
    
    def update(self, request, *args, **kwargs):
        if self.request.user.is_admin:
            return super().update(request, *args, **kwargs)
        raise NotFound()
    
    def destroy(self, request, *args, **kwargs):
        if self.request.user.is_admin:
            return super().destroy(request, *args, **kwargs)
        raise NotFound()
