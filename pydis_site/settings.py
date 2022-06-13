"""
Django settings for pydis_site project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import secrets
import sys
import warnings
from pathlib import Path
from socket import gethostbyname, gethostname

import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


env = environ.Env(
    DEBUG=(bool, False),
    SITE_DSN=(str, ""),
    BUILDING_DOCKER=(bool, False),
    STATIC_BUILD=(bool, False),
    GIT_SHA=(str, 'development'),
    TIMEOUT_PERIOD=(int, 5),
    GITHUB_TOKEN=(str, None),
)

GIT_SHA = env("GIT_SHA")
GITHUB_TOKEN = env("GITHUB_TOKEN")

sentry_sdk.init(
    dsn=env('SITE_DSN'),
    integrations=[DjangoIntegration()],
    send_default_pii=True,
    release=f"site@{GIT_SHA}"
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = env('DEBUG')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if DEBUG:
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
    SECRET_KEY = "yellow polkadot bikini"  # noqa: S105

    # Prevent verbose warnings emitted when passing a non-timezone aware
    # datetime object to the database, whilst we have time zone support
    # active. See the Django documentation for more details:
    # https://docs.djangoproject.com/en/dev/topics/i18n/timezones/
    warnings.filterwarnings(
        'error', r"DateTimeField .* received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields',
    )

elif 'CI' in os.environ:
    ALLOWED_HOSTS = ['*']
    SECRET_KEY = secrets.token_urlsafe(32)

    # See above. We run with `CI=true`, but debug unset in GitHub Actions,
    # so we also want to filter it there.
    warnings.filterwarnings(
        'error', r"DateTimeField .* received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields',
    )

else:
    ALLOWED_HOSTS = env.list(
        'ALLOWED_HOSTS',
        default=[
            'www.pythondiscord.com',
            'pythondiscord.com',
            gethostname(),
            gethostbyname(gethostname()),
            'site.default.svc.cluster.local',
        ],
    )
    SECRET_KEY = env('SECRET_KEY')

# Application definition
NON_STATIC_APPS = [
    'pydis_site.apps.api',
    'pydis_site.apps.staff',
] if not env("STATIC_BUILD") else []

INSTALLED_APPS = [
    *NON_STATIC_APPS,
    'pydis_site.apps.home',
    'pydis_site.apps.resources',
    'pydis_site.apps.content',
    'pydis_site.apps.events',
    'pydis_site.apps.redirect',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django_filters',
    'django_simple_bulma',
    'rest_framework',
    'rest_framework.authtoken',

    'django_distill',
]

if not env("BUILDING_DOCKER"):
    INSTALLED_APPS.append("django_prometheus")

NON_STATIC_MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
] if not env("STATIC_BUILD") else []

# Ensure that Prometheus middlewares are first and last here.
MIDDLEWARE = [
    *NON_STATIC_MIDDLEWARE,

    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django_prometheus.middleware.PrometheusAfterMiddleware'
]

ROOT_URLCONF = 'pydis_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'pydis_site', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "pydis_site.context_processors.git_sha_processor"
            ],
        },
    },
]

WSGI_APPLICATION = 'pydis_site.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': env.db(),
    'metricity': env.db('METRICITY_DB_URL'),
} if not env("STATIC_BUILD") else {}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'pydis_site', 'static')]
STATIC_ROOT = env('STATIC_ROOT', default='/app/staticfiles')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    'django_simple_bulma.finders.SimpleBulmaFinder',
]

if DEBUG:
    PARENT_HOST = env('PARENT_HOST', default='pythondiscord.local:8000')

    if ":" in PARENT_HOST:
        ALLOWED_HOSTS.append(PARENT_HOST.split(":", 1)[0])
    else:
        ALLOWED_HOSTS.append(PARENT_HOST)
else:
    PARENT_HOST = env('PARENT_HOST', default='pythondiscord.com')

# Django REST framework
# https://www.django-rest-framework.org
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissions',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

# Logging
# https://docs.djangoproject.com/en/2.1/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '%(asctime)s | %(process)d:%(thread)d | %(module)s | %(levelname)-8s | %(message)s'
            )
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': env(
                'LOG_LEVEL',
                default=(
                    # If there is no explicit `LOG_LEVEL` set,
                    # use `DEBUG` if we're running in debug mode but not
                    # testing. Use `ERROR` if we're running tests, else
                    # default to using `WARN`.
                    'INFO'
                    if DEBUG and 'test' not in sys.argv
                    else (
                        'ERROR'
                        if 'test' in sys.argv
                        else 'WARN'
                    )
                )
            )
        }
    }
}

# Custom settings for django-simple-bulma
BULMA_SETTINGS = {
    "variables": {  # If you update these colours, please update the notification.css file
        "primary": "#7289DA",    # Discord blurple
        "green": "#32ac66",      # Colour picked after Discord discussion
        "turquoise": "#7289DA",  # Blurple, because Bulma uses this regardless of `primary` above
        "blue": "#2482c1",       # Colour picked after Discord discussion
        "cyan": "#2482c1",       # Colour picked after Discord discussion (matches the blue)
        "purple": "#aa55e4",     # Apparently unused, but changed for consistency
        "red": "#d63852",        # Colour picked after Discord discussion

        "link": "$primary",

        "dimensions": "16 24 32 48 64 96 128 256 512",  # Possible image dimensions
        "navbar-height": "4.75rem",
        "footer-padding": "1rem 1.5rem 1rem",
        "tooltip-max-width": "30rem",
    },
    "extensions": [
        "bulma-dropdown",
        "bulma-navbar-burger",
    ],
    "fontawesome_token": "ff22cb6f41",
}

# Information about site repository
SITE_REPOSITORY_OWNER = "python-discord"
SITE_REPOSITORY_NAME = "site"
SITE_REPOSITORY_BRANCH = "master"

# Path for events pages
EVENTS_PAGES_PATH = Path(BASE_DIR, "pydis_site", "templates", "events", "pages")

# Path for content pages
CONTENT_PAGES_PATH = Path(BASE_DIR, "pydis_site", "apps", "content", "resources")

# Path for redirection links
REDIRECTIONS_PATH = Path(BASE_DIR, "pydis_site", "apps", "redirect", "redirects.yaml")

# How long to wait for synchronous requests before timing out
TIMEOUT_PERIOD = env("TIMEOUT_PERIOD")
