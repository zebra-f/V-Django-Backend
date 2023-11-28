import requests

# import jwt

from django.conf import settings
from google.oauth2.id_token import verify_token
from google.auth.transport.requests import Request


def exchange_code(code: str):
    # exchange the code
    url = "https://oauth2.googleapis.com/token"
    client_id = settings.OAUTH_PROVIDERS["GOOGLE"]["CLIENT_ID"]
    client_secret = settings.OAUTH_PROVIDERS["GOOGLE"]["CLIENT_SECRET"]
    redirect_uri = "http://127.0.0.1:8000/api-oauth/google/session/callback/"

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    response = requests.post(url, data=payload, headers=headers)

    # Check response status and handle accordingly
    if response.status_code == 200:
        json_response = response.json()
        result = verify_token(json_response["id_token"], Request())

        print(f"\n\n\n\n {result=} \n\n\n\n")

        # decoded_token = jwt.decode(
        #     token,
        #     algorithms=["RS256"],
        #     options={"verify_signature": False}
        # )
    else:
        # Error handling for unsuccessful response
        return None  # or raise an exception or handle the error as needed
