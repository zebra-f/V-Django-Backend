from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from core.users.validators import username_validator


class UsernameSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=32,
        validators=[
            username_validator,
            UniqueValidator(
                queryset=get_user_model().objects.all(),
                message="A user with this username already exists.",
            ),
        ],
    )
    password = serializers.CharField(
        max_length=128, required=False, write_only=True
    )

    def validate_password(self, value):
        validate_password(value)
        return value
