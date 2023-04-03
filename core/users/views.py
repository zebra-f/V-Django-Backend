from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404

from .serializers import (
    UserSerializer, 
    UserTokenPasswordResetSerializer, 
    UserVerifyEmailActivateUserSerializer
)
from .models import User
from .permissions import UserIsAuthorized, ForbiddenAction
from .emails.tokens import (
    ActivateUserVerifyEmailTokenGenerator,
    ActivateUserTokenGenerator,
    CustomPasswordResetTokenGenerator
)
from .services import Email
from .exceptions import ServiceUnavailable


class UserViewSet(viewsets.ModelViewSet):  
    queryset = User.objects.all() 
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    object_level_actions = [
        'retrieve',
        'destroy',
        'deactivate_user',
        'partial_update',
        ]
    forbidden_object_level_actions = [
        'update',
        'token_activate_user',
    ]

    def get_permissions(self):
        if self.action in ('list', 'create', 'token_password_reset', 'token_verify_email_activate_user', 'test',):
            self.permission_classes = [AllowAny]
        if self.action in self.object_level_actions:
            self.permission_classes = [UserIsAuthorized]
        if self.action in self.forbidden_object_level_actions:
            self.permission_classes = [ForbiddenAction]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        if self.action == 'token_password_reset':
            self.serializer_class = UserTokenPasswordResetSerializer
        if self.action == 'token_verify_email_activate_user':
            self.serializer_class = UserVerifyEmailActivateUserSerializer
        return super().get_serializer(*args, **kwargs)

    def check_token_get_user(self, request, token_generator):
        """ utility method """
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
    
    @action(methods=['get', 'post'], detail=False)
    def token_verify_email_activate_user(self, request):
        # a user requests a 'resend' of ActivateUserVerifiyEmailEmailMessage providing an email address
        # if the user exists and its .email_verified field is set to False, email is sent 
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = get_object_or_404(self.get_queryset(), email=serializer.data['email'])
            if user.email_verified:
                return Response(status=status.HTTP_409_CONFLICT)
            
            Email.send_activate_user_verify_email_token(user)
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
        # a user opens a verification link from the received 'welcome' email 
        else:
            token_generator = ActivateUserVerifyEmailTokenGenerator()
            user = self.check_token_get_user(request, token_generator)
            if user:
                user.activate_verify_email()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def token_activate_user(self, request):
        ''' NOT IN USE '''
        token_generator = ActivateUserTokenGenerator()
        user = self.check_token_get_user(request, token_generator)
        if user:
            user.activate()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def deactivate_user(self, request, pk=None):
        user = self.get_object()
        user.deactivate()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post', 'patch'], detail=False)
    def token_password_reset(self, request):
        # a user requests a password reset providing an email address
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = get_object_or_404(self.get_queryset(), email=serializer.data['email'])
            
            try:
                Email.send_password_reset_token(user)
            # Exception: <class 'kombu.exceptions.OperationalError'>
            except Exception:
                raise ServiceUnavailable()

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
        
        # a user submits a new password with the provided token
        if request.method == 'PATCH':
            token_generator = CustomPasswordResetTokenGenerator()
            user = self.check_token_get_user(request, token_generator)
            if user:
                serializer = self.get_serializer(user, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Admin views --- --- --- -->
    # Admin views --- --- --- -->
    # Admin views --- --- --- -->

    @action(methods=['get'], detail=True)
    def admin_activate_user(self, request, pk=None):
        user = self.get_object()
        user.activate()
        return Response(status=status.HTTP_200_OK)
    
    # To remove views --- --- --- -->
    # To remove views --- --- --- -->
    # To remove views --- --- --- -->

    @action(methods=['get', 'post'], detail=False)
    def test(self, request):
        data = {
            "test1": "test2"
        }
        return Response(status=status.HTTP_200_OK, data=data)


