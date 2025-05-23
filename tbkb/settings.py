"""
Django settings for tbkb project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path
from typing import List

import environ
import sentry_sdk
from django.core.exceptions import DisallowedHost
from sentry_sdk.integrations.django import DjangoIntegration

from . import settings_static

# make all static settings available from the start
vars().update({k: v for k, v in settings_static.__dict__.items() if k.isupper()})

# all variable settings defined below
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    SITE_HEADER=(str, "TbKb WHO administration (INTERNAL USE ONLY)"),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# The options are: aws, {other..}
DEPLOYMENT = env("DEPLOYMENT", default="local")
IS_DEPLOYMENT_AWS = DEPLOYMENT.lower() == "aws"

# The options are: development, production, testing.
ENVIRONMENT = env("ENVIRONMENT", default="production")
IS_PRODUCTION = ENVIRONMENT == "production"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

SITE_HEADER = env("SITE_HEADER")

CLOUDWATCH_LOGGROUP_SERVER = env(
    "CLOUDWATCH_LOGGROUP_SERVER",
    default="/backend/server",
)

CLOUDWATCH_LOGGROUP_ADMIN = env(
    "CLOUDWATCH_LOGGROUP_ADMIN",
    default="/backend/admin-activity",
)

CLOUDWATCH_LOGGROUP_DELEGATE = env(
    "CLOUDWATCH_LOGGROUP_DELEGATE",
    default="/backend/delegate-activity",
)


# SECURITY WARNING: don't run with debug turned on in production!
# False by default.
DEBUG = env("DEBUG")

ALLOWED_HOSTS: List[str] = env("ALLOWED_HOSTS")
CORS_ALLOWED_ORIGINS: List[str] = env("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

# Frontend domain and site name
FRONTEND_DOMAIN = env("FRONTEND_DOMAIN", default="localhost:3000")
SITE_NAME = env("SITE_NAME", default="FindDX TB-Kb")

# Skip import for django admin
IMPORT_EXPORT_SKIP_ADMIN_CONFIRM = env("IMPORT_EXPORT_SKIP_ADMIN_CONFIRM", default=True)

# Allow batch delete of large number of rows
DATA_UPLOAD_MAX_NUMBER_FIELDS = env("DATA_UPLOAD_MAX_NUMBER_FIELDS", default=10000)


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
if env.get_value("DB_HOST_PORT", default=None):
    db_host, db_port = env("DB_HOST_PORT").rsplit(":", 1)
else:
    db_host = env("DB_HOST", default="localhost")
    db_port = env("DB_PORT", default=5432)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": db_host,
        "PORT": db_port,
        "USER": env("DB_USER", default=None),
        "PASSWORD": env("DB_PASSWORD", default=None),
        "NAME": env("DB_NAME", default=None),
        "OPTIONS": {
            # Make DB able to see tables throughout all of our schemas.
            # Helpful with `manage.py inspectdb` command, since it does not support schemas.
            # https://code.djangoproject.com/ticket/28774
            "options": "-c search_path=public,genphensql,biosql",
        },
    },
}


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # for custom SSO admin login page template
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


#
# AWS config
#

# Access key/secret can be defined as app environment variables
# or any other way boto3 supports.
# One way or another, AWS connection should be available
# for sequencing data upload functionality,
# even for non-aws deployment.
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default=None)
# AWS region for boto3
AWS_DEFAULT_REGION = env("AWS_DEFAULT_REGION", default="us-east-1")
# Same AWS region for django-storages
AWS_S3_REGION_NAME = AWS_DEFAULT_REGION
AWS_S3_SIGNATURE_VERSION = "s3v4"
# AWS sequencing data bucket required anyway, whether it is local setup or cloud
# since submission flow has logic, tied to the way AWS S3 works.
AWS_SEQUENCING_DATA_BUCKET_NAME = env(
    "AWS_SEQUENCING_DATA_BUCKET_NAME",
    default=None,
)

#
# AWS deployment specific setup
#
if IS_DEPLOYMENT_AWS:
    # assuming production env app is always behind proxy,
    # this used to determine whether client request is secure
    SECURE_PROXY_SSL_HEADER = ("HTTP_CLOUDFRONT_FORWARDED_PROTO", "https")

    # django_iam_dbauth
    # Switch to IAM based DB authentication in AWS
    DATABASES["default"]["ENGINE"] = "django_iam_dbauth.aws.postgresql"
    DATABASES["default"]["OPTIONS"]["use_iam_auth"] = True
    DATABASES["default"]["OPTIONS"]["sslmode"] = "require"

    # django-allauth
    # to get right proto in links inside emails
    # assuming, that https will be only used in AWS
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True


#
# Email setup
#
#
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
# assume, we want email sending cooldown only on production
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 60 * 10 if IS_PRODUCTION else 10
if IS_DEPLOYMENT_AWS:
    # Setup AWS SES email.
    EMAIL_BACKEND = "django_ses.SESBackend"
    # Replace with this dummy backend while something is wrong with AWS SES
    # EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

    # We can possibly omit these settings,
    # if aws instance has direct access to SES without authorization
    AWS_SES_ACCESS_KEY_ID = env("AWS_SES_ACCESS_KEY_ID", default=AWS_ACCESS_KEY_ID)
    AWS_SES_SECRET_ACCESS_KEY = env(
        "AWS_SES_SECRET_ACCESS_KEY",
        default=AWS_SECRET_ACCESS_KEY,
    )
    AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME", default=AWS_DEFAULT_REGION)
    AWS_SES_REGION_ENDPOINT = env("AWS_SES_REGION_ENDPOINT")
else:
    # Setup local email.
    EMAIL_CONFIG = env.email("EMAIL_URL", default="consolemail://")
    vars().update(EMAIL_CONFIG)


#
# User-uploaded files
#
if IS_DEPLOYMENT_AWS:
    # django-storages
    # Make Django store media files in S3
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    # bucket name is required
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    # Directory inside the bucket, where uploaded files are stored.
    # By default, we don't use it.
    AWS_LOCATION = ""
    # Append a random string to a filename instead of overwriting file
    AWS_S3_FILE_OVERWRITE = False
else:
    # for non-aws deployment it is filesystem by default
    DEFAULT_FILE_STORAGE = env(
        "DEFAULT_FILE_STORAGE",
        default="django.core.files.storage.FileSystemStorage",
    )
    # where to store files locally
    MEDIA_ROOT = env("MEDIA_ROOT", default="tmp")


#
# Static files
#

# Django AWS storage for static files is disabled.
# "collectstatic" will be used locally, and then CI will copy static files on S3
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
STATIC_URL = env("STATIC_URL", default="static/")
# where "collectstatic" will collect static files
STATIC_ROOT = env("STATIC_ROOT", default=os.path.join(BASE_DIR, "static"))


#
# DRF config
#

REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Azure AD auth
        "django_auth_adfs.rest_framework.AdfsAccessTokenAuthentication",
    ],
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        # If you use MultiPartFormParser or FormParser, we also have a camel case version
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ],
    # Django global filter - disabled, we set filtering on per-view basis
    # "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    # Django global pagination - disabled, we set pagination on per-view basis
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # Per-view pagination class should have its own page_size property set,
    # means we need to always use custom pagination class
    # "PAGE_SIZE": 12,
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    "JSON_UNDERSCOREIZE": {
        "no_underscore_before_number": True,
    },
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO-8601 format
}

if not IS_PRODUCTION:
    # Non-production environment features
    # Enable DRF browsable API
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append(
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    )
    # enable session authentication in DRF browsable API
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].insert(
        0,
        "rest_framework.authentication.SessionAuthentication",
        # change for simpler access from Swagger
        # "rest_framework.authentication.BasicAuthentication",
    )


#
# Logging
#

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "basic": {
            "format": "%(asctime)s %(levelname)-7s %(name)s - %(message)s",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "basic",
        },
    },
    "loggers": {
        "": {
            # Default logging.
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.db.backends": {
            # Enable database queries logging with DEBUG=True.
            # (?)Somehow, django doesn't work if we put cloudwatch handler here...
            "level": "DEBUG",
            "handlers": ["console"],
            "filters": ["require_debug_true"],
            "propagate": False,
        },
        "django_auth_adfs": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "import_export": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

if IS_DEPLOYMENT_AWS:
    # Configure logging for CloudWatch

    # Use different formatter for default console logger - we don't need datetime there.
    LOGGING["formatters"].update(
        {
            "cloudwatch": {
                "format": "[%(process)d] (%(thread)d) %(levelname)-7s %(name)s - %(message)s",
            },
        },
    )
    LOGGING["handlers"]["console"]["formatter"] = "cloudwatch"

    # noinspection PyTypeChecker
    LOGGING["handlers"].update(
        {
            "cloudwatch_admin": {
                "class": "watchtower.CloudWatchLogHandler",
                "log_group_name": CLOUDWATCH_LOGGROUP_ADMIN,
                "level": "DEBUG",
            },
            "cloudwatch_delegate": {
                "class": "watchtower.CloudWatchLogHandler",
                "log_group_name": CLOUDWATCH_LOGGROUP_DELEGATE,
                "level": "DEBUG",
            },
            "cloudwatch_server": {
                "class": "watchtower.CloudWatchLogHandler",
                "log_group_name": CLOUDWATCH_LOGGROUP_SERVER,
                "level": "DEBUG",
            },
        },
    )

    # noinspection PyTypeChecker
    LOGGING["loggers"].update(
        {
            # named (it's called in different parts of app) TbKb admin log
            "tbkb.admin": {
                "level": "DEBUG",
                "handlers": ["cloudwatch_admin"],
            },
            # log delegate actions (all that happened in submission)
            "submission": {
                "level": "DEBUG",
                "handlers": ["cloudwatch_delegate"],
            },
            # webserver access logs
            "django.server": {
                "level": "DEBUG",
                "handlers": ["cloudwatch_server"],
            },
        },
    )


# using dummy defaults to pass library validation
ADFS_TENANT_ID = env("ADFS_TENANT_ID", default="00000000-0000-0000-0000-000000000000")
ADFS_CLIENT_ID = env("ADFS_CLIENT_ID", default="00000000-0000-0000-0000-000000000000")
ADFS_CLIENT_SECRET = env("ADFS_CLIENT_SECRET", default="secret-string")

AUTH_ADFS = {
    "AUDIENCE": ADFS_CLIENT_ID,
    "CLIENT_ID": ADFS_CLIENT_ID,
    "CLIENT_SECRET": ADFS_CLIENT_SECRET,
    "CLAIM_MAPPING": {
        "first_name": "given_name",
        "last_name": "family_name",
        # email claim can be missing for those accounts who don't have associated email
        "email": "email",
    },
    # Django counts app role with value "admins" group user as a superuser.
    # App registrations > {app name} > App roles
    "GROUP_TO_FLAG_MAPPING": {
        "is_superuser": "admins",
        "is_staff": "admins",
    },
    "GROUPS_CLAIM": "roles",
    "MIRROR_GROUPS": True,
    # MS recommends to use sub/oid for identification purposes.
    # sub is unique within single application, when oid is unique across all applications.
    # https://learn.microsoft.com/en-us/azure/active-directory/develop/id-token-claims-reference
    "USERNAME_CLAIM": "oid",
    "TENANT_ID": ADFS_TENANT_ID,
    "RELYING_PARTY_ID": ADFS_CLIENT_ID,
}

# Where to head a user for login.
# No need since we don't use django frontend.
# LOGIN_URL = "django_auth_adfs:login"

# Where to redirect a user after login.
# Meaning that django login happens only for admin section,
# we redirect him directly there.
LOGIN_REDIRECT_URL = "/admin/"


if IS_PRODUCTION:
    # Production environment features

    # Entrez API key/email AWS secret ARN.
    # Used to pour biosql schema.
    # Expected "email" and "api_key" keys.
    ENTREZ_SECRET_ARN = env("ENTREZ_SECRET_ARN", default=None)


SENTRY_DSN = env("SENTRY_DSN", default=None)

if SENTRY_DSN:
    # Optionally, init Sentry
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        # TODO switch back on sometime
        ignore_errors=[DisallowedHost],
    )
