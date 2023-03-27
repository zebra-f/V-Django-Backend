from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from core.users.models import User, UserPersonalProfile
from .utils.tokens import CustomPasswordResetTokenGenerator, ActivateUserVerifyEmailTokenGenerator
from .tasks import email_message_task
from .exceptions import ServiceUnavailable


class PasswordValidatorMixin:
    def custom_validate_password(self, instance, password):
        try:
            validate_password(password, instance)
        except ValidationError as e:
            raise DRFValidationError({'password': e.messages})
        return password


class EmailMessageMixin:
    def email_token(self, instance, token_generator, email_class_name: str):
        encoded_pk = urlsafe_base64_encode(force_bytes(instance.pk))
        token = token_generator.make_token(instance)
        try:
            email_message_task.delay(
                encoded_pk=encoded_pk, 
                token=token,  
                to=[instance.email],
                email_class_name=email_class_name
                )
        # Exception: <class 'kombu.exceptions.OperationalError'>
        except Exception:
            raise ServiceUnavailable()


class UserSerializer(serializers.ModelSerializer, PasswordValidatorMixin, EmailMessageMixin):
    new_password = serializers.CharField(required=False, max_length=128, write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'new_password']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}}

    def create(self, validated_data):
        instance = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        password = self.custom_validate_password(instance, validated_data['password'])
        instance.set_password(password)

        token_generator = ActivateUserVerifyEmailTokenGenerator()
        self.email_token(instance, token_generator, 'ActivateVerifiyUserEmailMessage')

        instance.save()
        user_personal_profile = UserPersonalProfile(
            user=instance
        )
        user_personal_profile.save()
        return instance

    def update(self, instance, validated_data):
        """
        As of now a user can only update its password via PATCH method.
        POST method disabled.
        """
        if validated_data.get('password') and validated_data.get('new_password'):
            # checks if a current password is correct
            if instance.check_password(validated_data.get('password')):
                # validates and sets a new password
                new_password = self.custom_validate_password(instance, validated_data['new_password'])
                instance.set_password(new_password)
                instance.save()
            else:
                raise DRFValidationError({'password': 'Wrong password'})
        else:
            raise DRFValidationError({
                'password': ['This field is required.'],
                'new_password': ['This field is required.']
                })
        return instance


class UserPasswordResetSerializer(serializers.Serializer, PasswordValidatorMixin, EmailMessageMixin):
    password = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
            
    def email_is_valid(self, validated_data, queryset):
        if not validated_data.get('email'):
            raise DRFValidationError({'email': ['This field is required.']})
        user = get_object_or_404(queryset, email=validated_data['email'])
        return user

    def send_reset_password_email(self, instance):
        token_generator = CustomPasswordResetTokenGenerator()
        self.email_token(instance, token_generator, 'PasswordResetEmailMessage')

    def update(self, instance, validated_data):
        if not validated_data.get('password'):
            raise DRFValidationError({'password': ['This field is required.']})
        password = self.custom_validate_password(instance, validated_data['password'])
        instance.set_password(password)
        instance.save()
        return instance