import hashlib
import os
import secrets


from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..decorators import check_oauth_enabled
from .services import exchange_code


@api_view(["GET"])
@check_oauth_enabled("GOOGLE")
def session_login(request):
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    request.session["state"] = state

    nonce = secrets.token_hex(23)
    uri = request.build_absolute_uri(reverse("google-session-callback"))

    return redirect(
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        f"client_id={settings.OAUTH_PROVIDERS['GOOGLE']['CLIENT_ID']}&"
        "scope=openid%20email&"
        f"redirect_uri={uri}&"
        f"state={state}&"
        f"nonce={nonce}"
    )


@api_view(["GET", "POST"])
def session_callback(request):
    """
    This view should never be directly called.
    """
    if request.method == "GET":
        query_params = request.query_params
        state = query_params.get("state", None)
        code = query_params.get("code", None)
        scope = query_params.get("scope", None)

        print(f"{state=}, {code=}, {scope=}")

        if not request.session or not request.session["state"]:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not state or not code or not scope:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.session["state"] != state:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        exchange_code(code)

        return Response({"message": "GET CALLBACK CALLED"})
    elif request.method == "POST":
        return Response({"message": "Got some data!", "data": request.data})
    else:
        return Response({"message": "Hello, world!"})
