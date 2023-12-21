import hashlib
import os
import secrets
import importlib

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.exceptions import ValidationError

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny

from ..decorators import check_oauth_enabled
from .services import exchange_code, get_code_and_validate_params
from .serializers import UsernameSerializer
from ...utils import set_refresh_cookie


@api_view(["GET"])
@check_oauth_enabled("GOOGLE")
def session_login(request):
    state = hashlib.sha256(os.urandom(1024)).hexdigest()

    request.session["state"] = state

    nonce = secrets.token_hex(23)
    callback_url = request.build_absolute_uri(
        reverse("google-session-callback")
    )
    return redirect(
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        f"client_id={settings.OAUTH_PROVIDERS['GOOGLE']['CLIENT_ID']}&"
        "scope=openid%20email&"
        f"redirect_uri={callback_url}&"
        f"state={state}&"
        f"nonce={nonce}"
    )


class GoogleSessionCallback(generics.GenericAPIView):
    """
    (Used for manual testing)- should never be directly called.
    Instead use `session_login` endpoint and follow instructions.
    """

    serializer_class = UsernameSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        code, valid = get_code_and_validate_params(request)
        if not valid:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        redirect_uri = request.build_absolute_uri(
            reverse("google-session-callback")
        )
        decoded_tokens = exchange_code(code, redirect_uri)

        email = decoded_tokens["email"]
        email_verified: bool = decoded_tokens["email_verified"]

        User = get_user_model()
        user = User.objects.filter(email=email).first()

        if user:
            if "Google" not in user.oauth_providers:
                user.oauth_providers.append("Google")
                user.save()
            try:
                login(request, user)
                return redirect("user-whoami")
            except Exception as e:
                return Response({"message": "Something went wrong."})
        else:
            request.session["user_email"] = email
            request.session["user_email_verified"] = email_verified
            return Response(
                {
                    "message": (
                        "Provide your username in the form under this message"
                        "(optionally, you can set a password to enable logging in directly with your email and password)."
                    )
                }
            )

    def post(self, request, *args, **kwargs):
        if (
            not request.session
            or not "user_email" in request.session
            or not "user_email_verified" in request.session
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            password = None
            if "password" in data:
                password = data["password"]

            User = get_user_model()
            try:
                user = User.objects.create_oauth_user(
                    email=request.session["user_email"],
                    email_verified=request.session["user_email_verified"],
                    username=data["username"],
                    oauth_provider="Google",
                    password=password,
                )
            except ValidationError as e:
                return Response(e)

            login(request, user)
            return redirect("user-whoami")
        else:
            return Response(serializer.errors)


@api_view(["GET"])
@check_oauth_enabled("GOOGLE")
def token_login(request):
    state = hashlib.sha256(os.urandom(1024)).hexdigest()

    # 20 min
    request.session.set_expiry(1200)
    request.session["state"] = state

    nonce = secrets.token_hex(23)
    callback_url = "http://127.0.0.1:5173/openid/googleredirect/"
    redrect_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        f"client_id={settings.OAUTH_PROVIDERS['GOOGLE']['CLIENT_ID']}&"
        "scope=openid%20email&"
        f"redirect_uri={callback_url}&"
        f"state={state}&"
        f"nonce={nonce}"
    )
    return Response(data={"redirect_url": redrect_url})


class GoogleTokenCallback(generics.GenericAPIView):
    serializer_class = UsernameSerializer
    permission_classes = [AllowAny]

    def finalize_response(self, request, response, *args, **kwargs):
        response = set_refresh_cookie(response)
        return super().finalize_response(request, response, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        code, valid = get_code_and_validate_params(request)
        if not valid:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        redirect_uri = "http://127.0.0.1:5173/openid/googleredirect/"
        decoded_tokens = exchange_code(code, redirect_uri)

        email = decoded_tokens["email"]
        email_verified: bool = decoded_tokens["email_verified"]

        User = get_user_model()
        user = User.objects.filter(email=email).first()

        if user:
            if "Google" not in user.oauth_providers:
                user.oauth_providers.append("Google")
                user.save()
            for path in settings.AUTHENTICATION_BACKENDS:
                module_name, class_name = path.rsplit(".", 1)
                module = importlib.import_module(module_name)
                AuthenticationBackend = getattr(module, class_name)
                if not AuthenticationBackend().user_can_authenticate(user):
                    return Response(
                        {
                            "message": "No active account found with the given credentials"
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            try:
                return Response({"message": "logged in"}, status=200)
                # Log in user !!!!
                # log in user !!!!
                # Log in user !!!!
            except Exception as e:
                return Response({"message": "Something went wrong."})
        else:
            request.session["user_email"] = email
            request.session["user_email_verified"] = email_verified
            return Response(
                {
                    "message": (
                        "Provide your username in the form under this message"
                        "(optionally, you can set a password to enable logging in directly with your email and password)."
                    )
                }
            )

    def post(self, request, *args, **kwargs):
        if (
            not request.session
            or not "user_email" in request.session
            or not "user_email_verified" in request.session
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            password = None
            if "password" in data:
                password = data["password"]

            User = get_user_model()
            try:
                user = User.objects.create_oauth_user(
                    email=request.session["user_email"],
                    email_verified=request.session["user_email_verified"],
                    username=data["username"],
                    oauth_provider="Google",
                    password=password,
                )
            except ValidationError as e:
                return Response(e)

            login(request, user)
            return redirect("user-whoami")
        else:
            return Response(serializer.errors)
