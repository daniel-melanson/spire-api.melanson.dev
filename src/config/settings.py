"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from distutils.util import strtobool
from pathlib import Path

from celery.schedules import crontab


def get_bool_env(key, default=False):
    if key in os.environ:
        return strtobool(os.environ[key])

    return default


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool_env("DEBUG", True)

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]


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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "spire"),
        "USER": os.environ.get("POSTGRES_USER", "spire_db_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "password"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
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

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "..", "static")

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# rest_framework

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
}

MINUTE = 60
HOUR = MINUTE * 60

VIEW_CACHE_TTL = MINUTE if DEBUG else os.environ.get("VIEW_CACHE_TTL", 3 * HOUR)

# spire.scraper

SCRAPER_DEBUG = get_bool_env("SCRAPER_DEBUG", False)
SCRAPER_HEADLESS = get_bool_env("SCRAPER_HEADLESS", True)
SCRAPER_SKIP_OLD_TERMS = get_bool_env("SCRAPER_SKIP_OLD_TERMS", True)

# Logging

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
            "filename": "./logs/debug/scrape-debug-results.log",
            "delay": True,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "scrape_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./logs/info/scrape-results.log",
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
            "level": "DEBUG" if SCRAPER_DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Caching
# https://docs.djangoproject.com/en/4.0/topics/cache/
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# Celery
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
CELERY_broker_url = REDIS_URL
result_backend = REDIS_URL
# beat_schedule = {
#     "scrape-courses": {
#         "task": "spire.tasks.scrape",
#         "schedule": crontab(minute=0, hour=0, day_of_week="*/14", day_of_month="*", month_of_year="*"),
#         "args": ("ScrapeCoverage.SubjectsAndCourses", False),
#     },
#     "scrape-sections": {
#         "task": "spire.tasks.scrape",
#         "schedule": crontab(minute=0, hour=0, day_of_week="*/7", day_of_month="*", month_of_year="*"),
#         "args": (ScrapeCoverage.Sections, False),
#     },
#     "quick-scrape-sections": {
#         "task": "spire.tasks.scrape",
#         "schedule": crontab(minute=0, hour="*/", day_of_week="*", day_of_month="*", month_of_year="*"),
#         "args": (ScrapeCoverage.Sections, True),
#     },
# }
