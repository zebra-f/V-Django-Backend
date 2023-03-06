from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenBlacklistSerializer
from rest_framework_simplejwt.exceptions import InvalidToken


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
    