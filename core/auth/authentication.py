from  django.contrib.auth.backends import ModelBackend
from rest_framework import exceptions


# class AuthenticationRules:

#     @staticmethod
#     def user_exists(user):
#         return user is not None

#     @staticmethod
#     def email_verified(user):
#         return user is not None and user.email_verified

#     @staticmethod
#     def is_active(user):
#         return user is not None and user.is_active


class CustomModelBackend(ModelBackend):

    def user_can_authenticate(self, user) -> bool:
        """
        Reject users with is_active=False and email_verified=False. Custom user models that don't have
        that attribute are allowed.
        """
        email_verified = getattr(user, "email_verified", None)
        if email_verified is not None and not email_verified:
            raise exceptions.AuthenticationFailed(
                "Email address not verified",
                "email_not_verified",
            )
        return super().user_can_authenticate(user)