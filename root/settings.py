"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path


def get_bool_env(key):
    if key in os.environ:
        return os.environ[key].lower() in ("true", "t", "yes", "on", "1")

    return False


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool_env("DEBUG")

ALLOWED_HOSTS = [] if DEBUG else ["spire-api.melanson.dev", "spire-api.herokuapp.com"]


# Application definition

INSTALLED_APPS = [
    "rest_framework",
    "django_filters",
    "spire",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "root.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["./root/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "root.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {
            "service": "spire_service",
            "passfile": ".pg_pass",
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
}

DEBUG_SCRAPER = get_bool_env("DEBUG_SCRAPER")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s - %(message)s",
            "style": "%",
        },
    },
    "handlers": {
        "scrape_debug_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./logs-debug/scrape-debug-results.log",
            "delay": True,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "scrape_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./logs/scrape-results.log",
            "delay": True,
            "backupCount": 10,
            "formatter": "verbose",
            "level": "INFO",
        },
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "spire.scraper": {
            "handlers": ["scrape_handler", "scrape_debug_handler"],
            "level": "DEBUG" if DEBUG_SCRAPER else "INFO",
            "propagate": False,
        },
    },
}

HEADLESS = get_bool_env("HEADLESS_SCRAPER")
