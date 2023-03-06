from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)

from .auth.views import CustomTokenRefreshView, LogoutView, LoginView
from .users.urls import router as users_router


# API Root
router = DefaultRouter()
router.registry.extend(users_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    path('api/', include(router.urls)),

    path('api/token/obtainpair/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/token/obtainpair/login/', LoginView.as_view(), name='login'),
    path('api/token/blacklist/logout/', LogoutView.as_view(), name='logout'),
    path('api/token/blacklist/refresh/', CustomTokenRefreshView.as_view(), name='refresh')
]
