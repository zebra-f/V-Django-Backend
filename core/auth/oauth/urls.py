from django.urls import path
from .google.views import (
    session_login as google_session_login,
    GoogleSessionCallback,
)

urlpatterns = [
    path(
        "api-oauth/google/session/login/",
        google_session_login,
        name="google-session-login",
    ),
    path(
        "api-oauth/google/session/callback/",
        GoogleSessionCallback.as_view(),
        name="google-session-callback",
    ),
]
