from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly

from django.shortcuts import get_object_or_404

from .models import Speed, SpeedBookmark, SpeedFeedback
from .permissions import UserIsAuthorized, ForbiddenAction, UserIsAuthor
from .serializers import SpeedSerializer


class SpeedViewSet(viewsets.ModelViewSet):
    queryset = Speed
    serializer_class = SpeedSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    object_level_actions = [
        'create'
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
        if self.action in self.object_level_actions:
            self.permission_classes = [UserIsAuthorized, UserIsAuthor]
        return super().get_permissions()
    

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



