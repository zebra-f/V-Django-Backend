from django.core.mail import EmailMessage
from django.conf import settings

CLIENT_BASE_URL = settings.CLIENT_BASE_URL


class ActivateUserVerifiyEmailEmailMessage(EmailMessage):
    def __init__(self, *args, encoded_pk=None, token=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoded_pk = encoded_pk
        self.token = token
        self.subject = """Sovertis - Activation"""
        self.body = f"""Welcome to Sovertis,
        To activate your account visit:  
            {CLIENT_BASE_URL}verifyemail/?id={self.encoded_pk}&token={self.token}
        \n
        If you didn't request this, you can safely ignore this message.
        Best regards, Sovertis.

        Contact email: contact@sovertis.com
        """
        self.reply_to = ["contact@sovertis.com"]


class ActivateUserEmailMessage(EmailMessage):
    def __init__(self, *args, encoded_pk=None, token=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoded_pk = encoded_pk
        self.token = token
        self.subject = """Activation email"""
        self.body = "Not in use."
        self.reply_to = ["contact@sovertis.com"]


class PasswordResetEmailMessage(EmailMessage):
    def __init__(self, *args, encoded_pk=None, token=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoded_pk = encoded_pk
        self.token = token
        self.subject = """Sovertis - Password Reset"""
        self.body = f"""Hello,
        It seems like you've forgotten your password. No worries! Visit the link below to reset it:
            {CLIENT_BASE_URL}passwordreset/?id={self.encoded_pk}&token={self.token}
        \n
        If you didn't request this, you can safely ignore this message.
        Best ragards, Sovertis.

        Contact email: contact@sovertis.com
        """
        self.reply_to = ["contact@sovertis.com"]
