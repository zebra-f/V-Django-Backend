from .utils.tokens import CustomPasswordResetTokenGenerator, ActivateUserVerifyEmailTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .exceptions import ServiceUnavailable
from .tasks import email_message_task


class Email:
    @staticmethod
    def send_activate_user_verify_email_token(instance):
        encoded_pk = urlsafe_base64_encode(force_bytes(instance.pk))
        token = ActivateUserVerifyEmailTokenGenerator().make_token(instance)
        try:
            email_message_task.delay(
                encoded_pk=encoded_pk, 
                token=token,  
                to=[instance.email],
                email_class_name='ActivateVerifiyUserEmailMessage'
                )
        # Exception: <class 'kombu.exceptions.OperationalError'>
        except Exception:
            raise ServiceUnavailable()
    
    @staticmethod
    def send_password_reset_token(instance):
        encoded_pk = urlsafe_base64_encode(force_bytes(instance.pk))
        token = CustomPasswordResetTokenGenerator().make_token(instance)
        try:
            email_message_task.delay(
                encoded_pk=encoded_pk, 
                token=token,  
                to=[instance.email],
                email_class_name='PasswordResetEmailMessage'
                )
        # Exception: <class 'kombu.exceptions.OperationalError'>
        except Exception:
            raise ServiceUnavailable()