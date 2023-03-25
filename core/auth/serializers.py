from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from rest_framework import exceptions
from rest_framework_simplejwt.serializers import (TokenRefreshSerializer, 
                                                  TokenBlacklistSerializer, 
                                                  TokenObtainSerializer,
                                                  TokenObtainPairSerializer
                                                  )                   
from rest_framework_simplejwt.exceptions import InvalidToken
from .authentication import AuthenticationRules


class CustomTokenObtainSerializer(TokenObtainSerializer):
    
    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass
        
        # Returns `None` if a users doesn't exist or is not active.
        self.user = authenticate(**authenticate_kwargs)

        # custom rules
        auth_rules = AuthenticationRules()
        if not auth_rules.user_exists(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )
        if not auth_rules.email_verified(self.user):
            raise exceptions.AuthenticationFailed(
                "Email address not verified",
                "email_not_verified",
            )
        # Should never reach this even if a user is not active.
        if not auth_rules.is_active(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        return {}
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer, CustomTokenObtainSerializer):
    pass


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    # Previously requeired JSON refresh field no longer needed.
    refresh = None
    
    def validate(self, attrs):
        request = self.context['request']
        attrs['refresh'] = request.COOKIES.get('refresh')
        if attrs['refresh']:
            data = super().validate(attrs)
            return data
        else:
            raise InvalidToken('No valid token has been found in cookies')
    

class LogoutSerializer(TokenBlacklistSerializer):
    refresh = None

    def validate(self, attrs):
        request = self.context['request']
        attrs['refresh'] = request.COOKIES.get('refresh')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidToken('No valid token has been found in cookies')
    