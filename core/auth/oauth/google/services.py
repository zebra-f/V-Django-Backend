import requests

# import jwt

from django.conf import settings

from google.oauth2.id_token import verify_token
from google.auth.transport.requests import Request


def get_code_and_validate_params(request) -> (str, bool):
    """
    Ensures that Google's callback request is valid.
    """
    query_params = request.query_params
    state = query_params.get("state", None)
    code = query_params.get("code", None)
    scope = query_params.get("scope", None)

    print(f"\n{state=}, {code=}, {scope=}\n")

    is_valid = True
    if not request.session or not "state" in request.session:
        is_valid = False
    if not state or not code or not scope:
        is_valid = False
    if request.session["state"] != state:
        is_valid = False

    return code, is_valid


def exchange_code(code: str, redirect_uri: str) -> dict:
    url = "https://oauth2.googleapis.com/token"
    client_id = settings.OAUTH_PROVIDERS["GOOGLE"]["CLIENT_ID"]
    client_secret = settings.OAUTH_PROVIDERS["GOOGLE"]["CLIENT_SECRET"]

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        decoded_token = verify_token(json_response["id_token"], Request())
        # decoded_token fields/keys
        # "iss", "azp", "aud", "sub", "email", "email_verified", "at_hash", "nonce", "iat", "exp"
        return decoded_token
        # decoded_token = jwt.decode(
        #     token,
        #     algorithms=["RS256"],
        #     options={"verify_signature": False}
        # )
    else:
        return None
