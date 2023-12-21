from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import IsAuthenticated

from django.utils import timezone

from .serializers import CustomTokenRefreshSerializer, LogoutSerializer
from ..users.models import User
from .utils import set_refresh_cookie


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = User.objects.get(email=request.data["email"])
            user.last_login = timezone.now()
            user.save()

        return response

    def finalize_response(self, request, response, *args, **kwargs):
        response = set_refresh_cookie(response)
        return super().finalize_response(request, response, *args, **kwargs)


class LogoutView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = LogoutSerializer
    queryset = User.objects.all()


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
