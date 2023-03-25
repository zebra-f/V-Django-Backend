class AuthenticationRules:

    @staticmethod
    def user_exists(user):
        return user is not None

    @staticmethod
    def email_verified(user):
        return user is not None and user.email_verified

    @staticmethod
    def is_active(user):
        return user is not None and user.is_active