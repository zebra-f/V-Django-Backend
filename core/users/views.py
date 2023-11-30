from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .serializers import (
    UserSerializer,
    UserTokenPasswordResetSerializer,
    UserVerifyEmailActivateUserSerializer,
)
from .models import User
from .permissions import UserIsAuthorized, ForbiddenAction
from .emails.tokens import (
    ActivateUserVerifyEmailTokenGenerator,
    ActivateUserTokenGenerator,
    CustomPasswordResetTokenGenerator,
)
from .services import Email
from .exceptions import ServiceUnavailable


class UserViewSet(viewsets.ModelViewSet):
    # ModelViewSet (3) attributes
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    # custom attribute
    not_allowed_http_method_names = ["put"]
    # ModelViewSet attribute
    http_method_names = []
    for method_name in viewsets.ModelViewSet.http_method_names:
        if method_name not in not_allowed_http_method_names:
            http_method_names.append(method_name)

    # custom attribute
    object_level_actions = [
        "retrieve",
        "destroy",
        "partial_update",
    ]
    # custom attribute
    forbidden_object_level_actions = [
        "deactivate_user",
        "update",
        "token_activate_user",
    ]

    def get_permissions(self):
        if (
            self.action
            in (
                "create",
                "token_password_reset",
                "token_verify_email_activate_user",
            )
            # explanation in the `list` method
            or self.action == "list"
        ):
            self.permission_classes = [AllowAny]
        if self.action in self.object_level_actions or self.action == "whoami":
            self.permission_classes = [UserIsAuthorized]
        if self.action in self.forbidden_object_level_actions:
            self.permission_classes = [ForbiddenAction]

        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        if self.action == "token_password_reset":
            self.serializer_class = UserTokenPasswordResetSerializer
        if self.action == "token_verify_email_activate_user":
            self.serializer_class = UserVerifyEmailActivateUserSerializer
        return super().get_serializer(*args, **kwargs)

    def check_token_get_user(
        self, request, token_generator: PasswordResetTokenGenerator
    ):
        """utility method"""
        encoded_pk = request.query_params.get("id")
        token = request.query_params.get("token")
        if encoded_pk and token:
            decoded_pk = force_str(urlsafe_base64_decode(encoded_pk))
            user = get_object_or_404(self.get_queryset(), pk=decoded_pk)
            if token_generator.check_token(user=user, token=token):
                return user
        return None

    def list(self, request, *args, **kwargs):
        # a workaround for the `DRF Browsable API` as the permission
        # `IsAdminUser` would remove the form used for the `create` method
        # this way users (anonymous and logged in) can use the form while
        # maintaining privacy of others by securing access to private data
        if request.user.is_anonymous or not request.user.is_admin:
            return Response(
                {"detail": 'Method "GET" not allowed.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().list(request, *args, **kwargs)

    @action(methods=["get"], detail=False)
    def whoami(self, request):
        """
        A view is designed to enable users to access their
        information without needing to provide
        a specific primary key (pk).
        """
        instance = request.user
        serializer = self.get_serializer_class()(instance)
        return Response(serializer.data)

    @action(methods=["get", "post"], detail=False)
    def token_verify_email_activate_user(self, request):
        # a user requests 'resend' of `ActivateUserVerifiyEmailEmailMessage` providing an email address
        # if the user exists and its `email_verified` field is set to False, email is sent
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = get_object_or_404(
                self.get_queryset(), email=serializer.data["email"]
            )
            if user.email_verified:
                return Response(status=status.HTTP_409_CONFLICT)

            Email.send_activate_user_verify_email_token(user)

            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_200_OK, headers=headers
            )
        # a user opens a verification link from the received 'welcome' email
        else:
            token_generator = ActivateUserVerifyEmailTokenGenerator()
            user = self.check_token_get_user(request, token_generator)
            if user:
                user.activate_verify_email()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=False)
    def token_activate_user(self, request):
        """NOT IN USE"""
        token_generator = ActivateUserTokenGenerator()
        user = self.check_token_get_user(request, token_generator)
        if user:
            user.activate()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=True)
    def deactivate_user(self, request, pk=None):
        """NOT IN USE"""
        user = self.get_object()
        user.deactivate()
        return Response(status=status.HTTP_200_OK)

    @action(methods=["post", "patch"], detail=False)
    def token_password_reset(self, request):
        # a user requests a password reset providing an email address
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = get_object_or_404(
                self.get_queryset(), email=serializer.data["email"]
            )

            try:
                Email.send_password_reset_token(user)
            # Exception: <class 'kombu.exceptions.OperationalError'>
            except Exception:
                raise ServiceUnavailable()

            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_200_OK, headers=headers
            )

        # a user submits a new password with the provided token
        if request.method == "PATCH":
            token_generator = CustomPasswordResetTokenGenerator()
            user = self.check_token_get_user(request, token_generator)
            if user:
                serializer = self.get_serializer(
                    user, data=request.data, partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=True)
    def admin_activate_user(self, request, pk=None):
        user = self.get_object()
        user.activate()
        return Response(status=status.HTTP_200_OK)
