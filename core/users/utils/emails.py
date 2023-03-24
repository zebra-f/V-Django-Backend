from django.core.mail import EmailMessage


class ActivateVerifiyUserEmailMessage(EmailMessage):
    def __init__(self, *args, encoded_pk=None, token=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoded_pk = encoded_pk
        self.token = token
        self.subject = '''Activation Verification email'''
        self.body = f'''To activate your account and to verify your email address visit:  
        http://127.0.0.1:8000/api/users/token_verify_email_activate_user/?id={self.encoded_pk}&token={self.token}'''
        self.reply_to = ['backend@example.com']


class ActivateUserEmailMessage(EmailMessage):
    
    def __init__(self, *args, encoded_pk=None, token=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoded_pk = encoded_pk
        self.token = token
        self.subject = '''Activation email'''
        self.body = f'''To activate your account visit:  
        http://127.0.0.1:8000/api/users/token_activate_user/?id={self.encoded_pk}&token={self.token}'''
        self.reply_to = ['backend@example.com']


class PasswordResetEmailMessage(EmailMessage):
    def __init__(self, *args, encoded_pk=None, token=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoded_pk = encoded_pk
        self.token = token
        self.subject = '''Password reset email'''
        self.body = f'''To reset your password visit:  
        http://127.0.0.1:8000/api/users/token_password_reset/?id={self.encoded_pk}&token={self.token}'''
        self.reply_to = ['backend@example.com']