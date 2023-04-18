from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly

from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedBookmark
from .permissions import UserIsAuthorized, ForbiddenAction, UserIsAuthor
from .serializers import SpeedSerializer, SpeedFeedbackSerializer
 

class SpeedViewSet(viewsets.ModelViewSet):
    queryset = Speed.objects.prefetch_related('feedback_counter')
    serializer_class = SpeedSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    object_level_actions = [
        'destroy',
        'update',
        'partial_update',
        ]
    
    def get_permissions(self):
        if self.action in (
            'list',
            'retrieve',
            ):
            self.permission_classes = [AllowAny]
        if self.action in (
            'create',
            ):
            self.permission_classes = [UserIsAuthorized]
        if self.action in self.object_level_actions:
            self.permission_classes = [UserIsAuthorized, UserIsAuthor]
        return super().get_permissions()

    def get_queryset(self):
        if self.action in (
            'list',
            'retrieve',
            ):
            if self.request.user.is_anonymous:
                return Speed.objects.filter(is_public=True).prefetch_related('feedback_counter')
            elif not self.request.user.is_admin:
                return Speed.objects.filter(
                     Q(is_public=True) | Q(author=self.request.user)
                    ).prefetch_related('feedback_counter')
            else:
                return super().get_queryset()
        return super().get_queryset()
    
    # Speed views --- --- --- -->
    # Speed views --- --- --- -->
    # Speed views --- --- --- -->

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = None
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        
        serializer_data = serializer.data
        if request.user:
            # storing all of speed ids
            id_vote_storage = {}
            for ordered_dict in serializer.data:
                id_vote_storage[ordered_dict['id']] = 0
            
            # making a query that returns a user vote and assining it to the id in the storage
            for speed_feedback in SpeedFeedback.objects.filter(speed__in=list(id_vote_storage.keys()), user=request.user):
                id_vote_storage[str(speed_feedback.speed.id)] = speed_feedback.vote
        
            # updating 'user_speed_feedback' field that's equal to = by default
            for ordered_dict in serializer_data:
                ordered_dict['user_speed_feedback'] = id_vote_storage[ordered_dict['id']]
        
        if page is not None:
            return self.get_paginated_response(serializer_data)
        else:
            return Response(serializer_data)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SpeedFeedbackViewSet(viewsets.ModelViewSet):
    queryset = SpeedFeedback.objects.all()
    serializer_class = SpeedFeedbackSerializer




