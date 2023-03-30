from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError as DRFValidationError


class PasswordValidatorMixin:
    def custom_validate_password(self, instance, password):
        try:
            validate_password(password, instance)
        except ValidationError as e:
            raise DRFValidationError({'password': e.messages})
        return password