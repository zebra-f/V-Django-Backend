from django.conf import settings

from rest_framework.response import Response


def check_oauth_enabled(oauth_provider: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if settings.OAUTH_PROVIDERS[oauth_provider]["disabled"]:
                return Response(
                    {
                        "message": f"{oauth_provider.lower().title()} is disabled."
                    }
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
