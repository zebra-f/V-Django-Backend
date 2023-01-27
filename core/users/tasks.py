# Celery tasks
from celery import shared_task

from core.users.utils.emails import ActivationEmailMessage, PasswordResetEmailMessage


@shared_task
def email_message_task(**kwargs):
    email_class_name = kwargs.pop('email_class_name', False)
    if not email_class_name:
        return
    if email_class_name == 'activation_email_message':
        email_message = ActivationEmailMessage(**kwargs)
        email_message.send(fail_silently=False)
    if email_class_name == 'password_reset_email_message':
        email_message = PasswordResetEmailMessage(**kwargs)
        email_message.send(fail_silently=False)