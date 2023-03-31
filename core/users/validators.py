from typing import Literal

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import User


def custom_validate_password(password: str, user: User, error_key: Literal['password', 'new_password']) -> str:
    ''' For use only in Django Rest Framework Serializer class '''
    try:
        validate_password(password, user)
    except ValidationError as e:
        raise DRFValidationError({error_key: e.messages})
    return password