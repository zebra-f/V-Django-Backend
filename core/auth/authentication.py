from django.contrib.auth.backends import ModelBackend


def can_authenticate(user) -> bool:
    if not user:
        return False

    email_verified = getattr(user, "email_verified", None)
    if email_verified is not None and not email_verified:
        return False

    is_banned = getattr(user, "is_banned", None)
    if is_banned:
        return False

    is_active = getattr(user, "is_active", None)
    if not is_active:
        return False

    return True


class CustomModelBackend(ModelBackend):
    def user_can_authenticate(self, user) -> bool:
        return super().user_can_authenticate(user) and can_authenticate(user)


def custom_simple_jwt_user_authentication_rule(user):
    """Redundant right now."""
    return can_authenticate(user)
