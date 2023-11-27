from django.urls import path, include
from .google.views import (
    session_callback as google_session_callback,
    session_login as google_session_login,
)

urlpatterns = [
    path(
        "api-oauth/google/session/login/",
        google_session_login,
        name="google-session-login",
    ),
    path(
        "api-oauth/google/session/callback/",
        google_session_callback,
        name="google-session-callback",
    ),
]
