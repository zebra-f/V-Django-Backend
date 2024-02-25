import requests

from django.conf import settings

from .emails.tokens import (
    CustomPasswordResetTokenGenerator,
    ActivateUserVerifyEmailTokenGenerator,
)
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from kombu.exceptions import OperationalError

from .tasks import (
    send_activate_user_verify_email_token_task,
    send_password_reset_token_task,
)
from .models import User


class Email:
    @staticmethod
    def send_activate_user_verify_email_token(instance: User):
        encoded_pk = urlsafe_base64_encode(force_bytes(instance.pk))
        token = ActivateUserVerifyEmailTokenGenerator().make_token(instance)
        try:
            send_activate_user_verify_email_token_task.delay(
                encoded_pk=encoded_pk,
                token=token,
                to=[instance.email],
            )
        except:
            raise OperationalError()

    @staticmethod
    def send_password_reset_token(instance: User):
        encoded_pk = urlsafe_base64_encode(force_bytes(instance.pk))
        token = CustomPasswordResetTokenGenerator().make_token(instance)
        try:
            send_password_reset_token_task.delay(
                encoded_pk=encoded_pk,
                token=token,
                to=[instance.email],
            )
        except:
            raise OperationalError()


def turnstile_token_is_valid(token: str) -> bool:
    secret = settings.CLOUDFLARE_TURNSTILE_SECRET_KEY

    form_data = {
        "secret": secret,
        "response": token,
    }
    response = requests.post(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify", data=form_data
    )
    json_response = response.json()

    return json_response.get("success", False)
