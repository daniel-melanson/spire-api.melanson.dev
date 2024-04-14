"""
Django settings for server project.
port 5432 failed: FATAL:  no pg_hba.conf entry for host "73.16.241.72", user "spire_worker", database "spire", no encryption
Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from distutils.util import strtobool
from pathlib import Path


def get_bool_env(key, default=False):
    if key in os.environ:
        return bool(strtobool(os.environ[key].lower()))

    return default


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool_env("DEBUG", True)

allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,0.0.0.0,127.0.0.1,[::1]")
ALLOWED_HOSTS = list(map(str.strip, allowed_hosts.split(",")))


# Application definition

INSTALLED_APPS = [
    "rest_framework",
    "django_filters",
    "spire",
    "corsheaders",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
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
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "password"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "OPTIONS": {"sslmode": "require"},
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

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_THROTTLE_CLASSES": ["spire.throttles.BlindRateThrottle"],
}

# spire.scraper

SCRAPER = {
    "SELENIUM_SERVER_URL": os.environ.get("SELENIUM_SERVER_URL", None),
    "DEBUG": DEBUG,
    # Skip terms that have already been scraped and wouldn't be reasonably updated
    "SKIP_OLD_TERMS": get_bool_env("SCRAPER_SKIP_OLD_TERMS", True),
    # Skip existing objects, unless information is different
    "SKIP_EXISTING": get_bool_env("SKIP_EXISTING", True),
}

# Logging


def ensure_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


ensure_exists(os.path.join(BASE_DIR, "..", "logs", "info"))
ensure_exists(os.path.join(BASE_DIR, "..", "logs", "debug"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "()": "spire.formatters.ProcessTimeFormatter",
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
            "formatter": "verbose",
        },
        "log_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/tmp/spire-api/spire-api.log",
            "delay": True,
            "backupCount": 10,
            "formatter": "verbose",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console"] if DEBUG else ["log_file"],
        "level": "INFO",
    },
    "loggers": {
        "spire.scraper": {
            "handlers": (
                ["scrape_handler", "scrape_debug_handler"]
                if SCRAPER["DEBUG"]
                else ["console"]
            ),
            "level": "DEBUG" if SCRAPER["DEBUG"] else "INFO",
            "propagate": False,
        },
    },
}

# Caching
# https://docs.djangoproject.com/en/4.0/topics/cache/

MINUTE = 60
HOUR = MINUTE * 60

CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_KEY_PREFIX = "spireapi"
CACHE_MIDDLEWARE_SECONDS = (
    MINUTE if DEBUG else int(os.environ.get("CACHE_MIDDLEWARE_SECONDS", 3 * HOUR))
)

if not DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379"),
        }
    }
