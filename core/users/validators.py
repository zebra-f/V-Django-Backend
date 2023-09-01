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
    # Specify max_length in the model/serializer field.
    regex=r"^[A-Za-z][A-Za-z0-9_]{2,}$",
    message=(
        "Username must begin with a letter. "
        "Username may consist of letters, numbers, and underscores. "
        "Username must be at least 3 characters in length."
    )
)