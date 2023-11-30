from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
    TokenBlacklistSerializer,
)

from rest_framework.exceptions import NotFound


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    # Previously requeired JSON refresh field no longer needed.
    refresh = None

    def validate(self, attrs):
        request = self.context["request"]
        attrs["refresh"] = request.COOKIES.get("refresh")
        if attrs["refresh"]:
            return super().validate(attrs)
        else:
            raise NotFound(
                "No valid refresh token has been found in cookies.",
                code="token_not_found",
            )


class LogoutSerializer(TokenBlacklistSerializer):
    # Previously requeired JSON refresh field no longer needed.
    refresh = None

    def validate(self, attrs):
        request = self.context["request"]
        attrs["refresh"] = request.COOKIES.get("refresh")
        if attrs["refresh"]:
            return super().validate(attrs)
        else:
            raise NotFound(
                "No valid refresh token has been found in cookies.",
                code="token_not_found",
            )
