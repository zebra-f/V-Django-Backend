from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.validators import UniqueValidator

from core.users.models import User, UserPersonalProfile
from .services import Email
from .validators import custom_validate_password, username_validator
from .exceptions import ServiceUnavailable


class UserSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        required=False, max_length=128, write_only=True
    )
    username = serializers.CharField(
        max_length=24,
        validators=[
            username_validator,
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with this username already exists.",
            ),
        ],
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "new_password",
            "created_at",
            "updated_at",
            "last_login",
            "oauth_providers",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "last_login",
            "oauth_providers",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            email=validated_data["email"], username=validated_data["username"]
        )
        password = custom_validate_password(
            validated_data["password"], user, "password"
        )
        user.set_password(password)

        try:
            Email.send_activate_user_verify_email_token(user)
        # Exception: <class 'kombu.exceptions.OperationalError'>
        except Exception:
            raise ServiceUnavailable()

        with transaction.atomic():
            user.save()
            user_personal_profile = UserPersonalProfile(user=user)
            user_personal_profile.save()

        return user

    def update(self, user, validated_data):
        """
        As of now a user can only update its password via PATCH method.
        PUT method disabled.
        """
        password = validated_data.get("password", None)
        new_password = validated_data.get("new_password", None)
        if password and new_password:
            # checks if the current password is correct
            if not user.check_password(password):
                raise DRFValidationError({"password": "Wrong password"})
            # validates a new password
            new_password = custom_validate_password(
                new_password, user, "new_password"
            )
            user.update_password(new_password)
        else:
            raise DRFValidationError(
                {
                    "password": ["This field is required."],
                    "new_password": ["This field is required."],
                }
            )
        return user

    def get_fields(self):
        fields = super().get_fields()
        if "request" in self.context and self.context["request"].method in [
            "POST"
        ]:
            del fields["new_password"]
        return fields


class UserTokenPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)

    def update(self, user, validated_data):
        """Aviable via the PATCH method"""
        new_password = validated_data.get("new_password", None)
        if not new_password:
            raise DRFValidationError(
                {"new_password": ["This field is required."]}
            )
        new_password = custom_validate_password(
            new_password, user, "new_password"
        )
        user.update_password(new_password)
        return user


class UserVerifyEmailActivateUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
