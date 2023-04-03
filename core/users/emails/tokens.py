from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivateUserVerifyEmailTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp: int) -> str:
        hash_value = super()._make_hash_value(user, timestamp)
        return hash_value + str(user.email_verified) + str(user.is_active)

    def check_token(self, user, token) -> bool:
        check_token_ = super().check_token(user, token)
        
        if check_token_:
            if user.is_active:
                return False
            if user.email_verified:
                return False
        
        return check_token_


class ActivateUserTokenGenerator(PasswordResetTokenGenerator): 
    def _make_hash_value(self, user, timestamp: int) -> str:
        hash_value = super()._make_hash_value(user, timestamp)
        return hash_value + str(user.is_active)


    def check_token(self, user, token) -> bool:
        check_token_ = super().check_token(user, token)

        if check_token_:
            if user.is_active:
                return False
        
        return check_token_


class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    pass
