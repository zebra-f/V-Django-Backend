from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings

from .serializers import CustomTokenRefreshSerializer, LogoutSerializer, CustomTokenObtainPairSerializer

from ..users.models import User


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.get(email=request.data['email'])
            user.last_login = timezone.now()
            user.save()
        
        return response

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            response.set_cookie(
                'refresh', 
                value=response.data['refresh'], 
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'], 
                path='/api/token/',
                httponly=True,
                samesite='Strict',
                secure=True,
                )
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)


class LogoutView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = LogoutSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        user = request.user
        user.last_logout = timezone.now()
        user.save()

        return super().post(request, *args, **kwargs) 


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

