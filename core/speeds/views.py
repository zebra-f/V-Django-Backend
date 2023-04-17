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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SpeedFeedbackViewSet(viewsets.ModelViewSet):
    queryset = SpeedFeedback.objects.all()
    serializer_class = SpeedFeedbackSerializer




