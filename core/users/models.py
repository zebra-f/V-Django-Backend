from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.utils.crypto import get_random_string
from django.contrib.auth.password_validation import validate_password

from uuid import uuid4


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **kwargs):
        """
        Creates and saves a User with the given email and password.
        **kwargs: other fields from User model including those inherited from Users's parent class PermissionsMixin.
        """
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have an username")
        if not password:
            raise ValueError("Users must have a password")

        user = self.model(
            email=self.normalize_email(email), username=username, **kwargs
        )
        # user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_oauth_user(
        self,
        email,
        email_verified: bool,
        username: str,
        oauth_provider: str,
        password=None,
    ):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have an username")

        user = self.model(
            email=self.normalize_email(email),
            email_verified=email_verified,
            username=username,
            oauth_providers=[oauth_provider],
        )
        user.is_active = True

        if password:
            # a user may opt for a password
            validate_password(password, user)
            user.set_password(password)
        else:
            user.set_password(get_random_string(length=40))

        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **kwargs):
        """
        Creates and saves a superuser with the given email and password.
        **kwargs: other fields from User model including those inherited from Users's parent class PermissionsMixin.
        """
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)

        if not kwargs.get("is_superuser"):
            raise ValueError("Superuser must have is_staff field set to True")

        if not kwargs.get("is_active"):
            raise ValueError(
                "Superuser must have is_superuser field set to True"
            )

        user = self.create_user(email, username, password=password, **kwargs)
        user.is_admin = True
        user.email_verified = True
        user.save(using=self._db)
        return user


def get_oauth_providers_default_list():
    return []


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        ordering = ["-created_at"]

    id = models.UUIDField(primary_key=True, default=uuid4)
    email = models.EmailField(_("email address"), max_length=255, unique=True)

    email_verified = models.BooleanField(default=False)

    username = models.CharField(
        _("username"), max_length=32, unique=True, db_index=True
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    last_login = models.DateTimeField(_("last login"), null=True)
    last_logout = models.DateTimeField(_("last logout"), null=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    # used as a login
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    # required for the creation of superuser
    REQUIRED_FIELDS = ["username"]

    # OAuth
    oauth_providers = ArrayField(
        models.CharField(max_length=40),
        size=10,
        default=get_oauth_providers_default_list,
    )

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        # All admins are staff
        return self.is_admin

    def update_password(self, new_password: str) -> None:
        self.set_password(new_password)
        self.save()

    def activate(self) -> None:
        self.is_active = True
        self.save()

    def deactivate(self) -> None:
        self.is_active = False
        self.save()

    def activate_verify_email(self) -> None:
        self.is_active = True
        self.email_verified = True
        self.save()


class UserPersonalProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="user_personal_profile",
        on_delete=models.CASCADE,
    )

    # blank: validation related
    first_name = models.CharField(
        _("first name"), max_length=64, null=True, blank=True
    )
    last_name = models.CharField(
        _("last name"), max_length=64, null=True, blank=True
    )

    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.user.email
