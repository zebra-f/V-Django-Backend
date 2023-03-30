from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.shortcuts import get_object_or_404

from core.users.models import User, UserPersonalProfile
from .services import Email


class UserSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=False, max_length=128, write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'new_password']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['email'],
            validated_data['username'],
            validated_data['password']
            )
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
        if validated_data.get('password') and validated_data.get('new_password'):
            if not user.update_password(validated_data['password'], validated_data['new_password']):
                raise DRFValidationError({'password': 'Wrong password'})
        else:
            raise DRFValidationError({
                'password': ['This field is required.'],
                'new_password': ['This field is required.']
                })
        return user


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
            
    def email_is_valid(self, validated_data, queryset):
        if not validated_data.get('email'):
            raise DRFValidationError({'email': ['This field is required.']})
        user = get_object_or_404(queryset, email=validated_data['email'])
        return user

    def send_reset_password_email(self, user):
        Email.send_password_reset_token(user)

    def update(self, user, validated_data):
        if not validated_data.get('password'):
            raise DRFValidationError({'password': ['This field is required.']})
        user.token_update_password(validated_data['password'])
        return user