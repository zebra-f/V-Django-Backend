from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.shortcuts import get_object_or_404

from core.users.models import User, UserPersonalProfile
from .services import Email
from .validators import custom_validate_password
from .exceptions import ServiceUnavailable

from rest_framework.exceptions import ValidationError as DRFValidationError


class UserSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=False, max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'new_password']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}}


    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        password = custom_validate_password(validated_data['password'], user, 'password')
        user.set_password(password)

        try:
            Email.send_activate_user_verify_email_token(user)
        # Exception: <class 'kombu.exceptions.OperationalError'>
        except Exception:
            raise ServiceUnavailable()
        
        user.save()
        
        user_personal_profile = UserPersonalProfile(
            user=user
        )
        user_personal_profile.save()
        return user

    def update(self, user, validated_data):
        """
        As of now a user can only update its password via PATCH method.
        POST method disabled.
        """
        password = validated_data.get('password', None)
        new_password = validated_data.get('new_password', None)
        if password and new_password:
            # checks if the current password is correct
            if not user.check_password(password):
                raise DRFValidationError({'password': 'Wrong password'})
            # validates a new password
            new_password = custom_validate_password(new_password, user, 'new_password')
            user.update_password(new_password)
        else:
            raise DRFValidationError({
                'password': ['This field is required.'],
                'new_password': ['This field is required.']
                })
        return user


class UserTokenPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def validate_email(self, value):
        return value
            
    def email_is_valid(self, validated_data, queryset) -> User:
        if not validated_data.get('email'):
            raise DRFValidationError({'email': ['This field is required.']})
        user = get_object_or_404(queryset, email=validated_data['email'])

        try:
            Email.send_password_reset_token(user)
        # Exception: <class 'kombu.exceptions.OperationalError'>
        except Exception:
            raise ServiceUnavailable()

    def update(self, user, validated_data):
        new_password = validated_data.get('new_password', None)
        if not new_password:
            raise DRFValidationError({'new_password': ['This field is required.']})
        new_password = custom_validate_password(new_password, user, 'new_password')
        user.update_password(new_password)
        return user