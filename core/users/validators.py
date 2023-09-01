from typing import Literal

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import User

# Serializers

def custom_validate_password(password: str, user: User, error_key: Literal['password', 'new_password']) -> str:
    ''' For use only in Django Rest Framework Serializer class '''
    try:
        validate_password(password, user)
    except ValidationError as e:
        raise DRFValidationError({error_key: e.messages})
    return password

# User.username (CharField)
username_validator = RegexValidator(
    regex=r"^[A-Za-z][A-Za-z0-9_]{3,29}$",
    message="""
            Username should start with an a letter,
            username can only contain letters, numbers, and underscores.
            username should have length of at least 5 characters
            """
)