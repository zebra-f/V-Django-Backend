from django.urls import path
from .google.views import (
    session_login as google_session_login,
    GoogleSessionCallback,
    token_login as google_token_login,
    GoogleTokenCallback,
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
    path(
        "api/token/google/login/",
        google_token_login,
        name="google-token-login",
    ),
    path(
        "api/token/google/callback/",
        GoogleTokenCallback.as_view(),
        name="google-token-callback",
    ),
]
