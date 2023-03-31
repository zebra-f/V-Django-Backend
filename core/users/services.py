from .utils.tokens import CustomPasswordResetTokenGenerator, ActivateUserVerifyEmailTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from kombu.exceptions import OperationalError

from .tasks import (send_activate_user_verify_email_token_task, 
                    send_password_reset_token_task
                    )


class Email:
    @staticmethod
    def send_activate_user_verify_email_token(instance):
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
    def send_password_reset_token(instance):
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