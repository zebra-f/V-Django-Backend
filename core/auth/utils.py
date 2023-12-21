from django.conf import settings


def set_refresh_cookie(response):
    if response.data.get("refresh"):
        response.set_cookie(
            "refresh",
            value=response.data["refresh"],
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            path="/api/token/",
            httponly=True,
            samesite="Strict",
            secure=True,
        )
        del response.data["refresh"]

    return response
