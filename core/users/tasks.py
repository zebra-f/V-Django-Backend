# Celery tasks
from celery import shared_task

from core.users.emails.messages import  (
    ActivateUserVerifiyEmailEmailMessage,
    ActivateUserEmailMessage,
    PasswordResetEmailMessage,
)


@shared_task
def send_activate_user_verify_email_token_task(**kwargs):
    email_message = ActivateUserVerifiyEmailEmailMessage(**kwargs)
    email_message.send(fail_silently=False)

@shared_task
def send_password_reset_token_task(**kwargs):
    email_message = PasswordResetEmailMessage(**kwargs)
    email_message.send(fail_silently=False)

@shared_task
def send_activate_user_token_task(**kwargs):
    ''' NOT IN USE '''
    email_message = ActivateUserEmailMessage(**kwargs)
    email_message.send(fail_silently=False)
