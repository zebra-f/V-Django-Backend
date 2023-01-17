from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, UserPasswordResetSerializer
from .models import User
from .permissions import UserIsAuthorized, ForbiddenAction
from .utils.tokens import activate_user_token_generator, custom_password_reset_token_generator


class UserViewSet(viewsets.ModelViewSet):  
    queryset = User.objects.all() 
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    object_level_actions = [
        'retrieve', 
        'destroy', 
        'deactivate', 
        'partial_update',
        ]
    forbidden_object_level_actions = [
        'update',
    ]

    def get_permissions(self):
        if self.action in ('list', 'create', 'token_activate_user', 'token_password_reset', 'test'):
            self.permission_classes = [AllowAny]
        if self.action in self.object_level_actions:
            self.permission_classes = [UserIsAuthorized]
        if self.action in self.forbidden_object_level_actions:
            self.permission_classes = [ForbiddenAction]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        if self.action == 'token_password_reset':
            self.serializer_class = UserPasswordResetSerializer
        return super().get_serializer(*args, **kwargs)

    def check_token_get_user(self, request, token_generator):
        encoded_pk = request.query_params.get('id')
        token = request.query_params.get('token')
        if encoded_pk and token:
            decoded_pk = force_str(urlsafe_base64_decode(encoded_pk))
            user = get_object_or_404(self.get_queryset(), pk=decoded_pk)
            if token_generator.check_token(user=user, token=token):
                return user
        return None
    
    # User views --- --- --- -->
    # User views --- --- --- -->
    # User views --- --- --- -->
    
    # [reminder] change method to POST
    @action(methods=['get'], detail=False)
    def token_activate_user(self, request):
        user = self.check_token_get_user(request, activate_user_token_generator)
        if user:
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def deactivate_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post', 'patch'], detail=False)
    def token_password_reset(self, request):
        # user requests a password reset
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.email_is_valid(serializer.data, self.get_queryset())
            serializer.send_reset_password_email(user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
        # user submits a new password with the provided token
        if request.method == 'PATCH':
            user = self.check_token_get_user(request, custom_password_reset_token_generator)
            if user:
                serializer = self.get_serializer(user, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
    @action(methods=['get', 'post'], detail=False)
    def test(self, request):
        data = {
            "test1": "test2"
        }
        return Response(status=status.HTTP_200_OK, data=data)

    # Admin views --- --- --- -->
    # Admin views --- --- --- -->
    # Admin views --- --- --- -->

    @action(methods=['get'], detail=True)
    def admin_activate_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(status=status.HTTP_200_OK)


