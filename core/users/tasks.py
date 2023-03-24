# Celery tasks
from celery import shared_task

from core.users.utils.emails import  (
    ActivateVerifiyUserEmailMessage,
    ActivateUserEmailMessage,
    PasswordResetEmailMessage,
)


@shared_task
def email_message_task(**kwargs):
    email_class_name = kwargs.pop('email_class_name', False)
    if not email_class_name:
        return
    if email_class_name == 'ActivateVerifiyUserEmailMessage':
        email_message = ActivateVerifiyUserEmailMessage(**kwargs)
        email_message.send(fail_silently=False)
    if email_class_name == 'ActivateUserEmailMessage':
        # currenlty not in use
        email_message = ActivateUserEmailMessage(**kwargs)
        email_message.send(fail_silently=False)
    if email_class_name == 'PasswordResetEmailMessage':
        email_message = PasswordResetEmailMessage(**kwargs)
        email_message.send(fail_silently=False)