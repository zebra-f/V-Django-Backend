from django.contrib.auth.backends import ModelBackend


class CustomModelBackend(ModelBackend):
    def user_can_authenticate(self, user) -> bool:
        """
        Reject users with is_active=False and email_verified=False. Custom user models that don't have
        that attribute are allowed.
        """
        email_verified = getattr(user, "email_verified", None)
        if email_verified is not None and not email_verified:
            return False
        return super().user_can_authenticate(user)
