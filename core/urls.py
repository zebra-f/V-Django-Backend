from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings

from .auth.views import CustomTokenRefreshView, LogoutView, LoginView
from .users.urls import router as users_router
from .speeds.urls import router as speeds_router
from .auth.oauth.urls import urlpatterns as oauth_urlpatterns


# API Root
router = DefaultRouter()
router.registry.extend(users_router.registry)
router.registry.extend(speeds_router.registry)

urlpatterns = [
    path(f"admin/{settings.ADMIN_URL_SEGMENT}/", admin.site.urls),
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),
    path("api/", include(router.urls)),
    #
    path("api/token/login/", LoginView.as_view(), name="login"),
    path("api/token/logout/", LogoutView.as_view(), name="logout"),
    path(
        "api/token/refresh/", CustomTokenRefreshView.as_view(), name="refresh"
    ),
]

urlpatterns += oauth_urlpatterns
