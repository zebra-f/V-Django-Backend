"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
from datetime import timedelta

import sys
import os

from django.core.exceptions import ImproperlyConfigured


def get_env_variable(variable_name: str) -> str:
    variable = os.environ.get(variable_name)
    if variable == None:
        raise ImproperlyConfigured(
            f"The {variable_name} environment variable is not set."
        )
    return variable


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

TESTING = sys.argv[1:2] == ["test"]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable("DJANGO_V_1_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(get_env_variable("DEBUG")))

ALLOWED_HOSTS = get_env_variable("ALLOWED_HOSTS").split(" ")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core.users",
    "core.speeds",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env_variable("POSTGRES_DB_NAME"),
        "USER": get_env_variable("POSTGRES_USER"),
        "PASSWORD": get_env_variable("POSTGRES_V_1_PASSWORD"),
        "HOST": get_env_variable("POSTGRES_HOST"),
        "PORT": get_env_variable("POSTGRES_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Django settings

# auth
AUTHENTICATION_BACKENDS = ["core.auth.authentication.CustomModelBackend"]
AUTH_USER_MODEL = "users.User"

# email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "backend@example.com"
ADMINS = [
    ("John Smith", "john@example.com"),
    # ('Jane Doe', 'jane@example.com'),
]

# PasswordResetTokenGenerator
PASSWORD_RESET_TIMEOUT = 172800  # 2 days in seconds


# logging
if not TESTING:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
                "style": "{",
            },
            "simple": {
                "format": "{levelname} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
            "speeds_debug_file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": os.path.join(
                    BASE_DIR, "logs", "speeds", "debug.log"
                ),
                "formatter": "verbose",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
                "email_backend": "django.core.mail.backends.console.EmailBackend",
                "include_html": False,
                "formatter": "verbose",
            },
        },
        "loggers": {
            "core.speeds": {
                "handlers": [
                    "speeds_debug_file",
                    "mail_admins",
                ],
                "level": "DEBUG",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    }


# Django Rest Framework settings

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=2),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "core.auth.authentication.custom_simple_jwt_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

CORS_ALLOWED_ORIGINS = get_env_variable("CORS_ALLOWED_ORIGINS").split(" ")
CORS_ALLOW_CREDENTIALS = True

# Celery settings

# CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
CELERY_BROKER_URL = get_env_variable("REDIS_URL")


# Redis cache settings

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": get_env_variable("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# Meilisearch settings

MEILISEARCH = {
    "disabled": bool(int(get_env_variable("MEILISEARCH_DISABLED"))) or TESTING,
    "MASTER_KEY": None,
    "URL": None,
}

if not MEILISEARCH["disabled"]:
    MEILISEARCH["MASTER_KEY"] = get_env_variable("MEILISEARCH_V_1_MASTER_KEY")
    MEILISEARCH["URL"] = get_env_variable("MEILISEARCH_URL")


# OAuth settings

OAUTH_PROVIDERS = {
    "GOOGLE": {
        "disabled": bool(int(get_env_variable("GOOGLE_OAUTH_DISABLED"))),
        "CLIENT_ID": None,
        "CLIENT_SECRET": None,
        "FRONTEND_CALLBACK_URL": None,
    }
}


if not OAUTH_PROVIDERS["GOOGLE"]["disabled"]:
    OAUTH_PROVIDERS["GOOGLE"]["CLIENT_ID"] = get_env_variable(
        "GOOGLE_OAUTH_CLIENT_ID"
    )
    OAUTH_PROVIDERS["GOOGLE"]["CLIENT_SECRET"] = get_env_variable(
        "GOOGLE_OAUTH_CLIENT_SECRET"
    )
    OAUTH_PROVIDERS["GOOGLE"]["FRONTEND_CALLBACK_URL"] = get_env_variable(
        "FRONTEND_CALLBACK_URL"
    )
