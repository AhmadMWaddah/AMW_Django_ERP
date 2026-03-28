"""
-- AMW Django ERP - Base Settings --

This module contains the core configuration shared across all environments.
Environment-specific settings should extend this module and override as needed.

Project: AMW Django ERP
Constitution: Constitution_AMW_DJ_ERP.md
"""

from pathlib import Path

import environ
from django.contrib.messages import constants as messages

# -- Build Paths --
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# -- Environment Setup --
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ""),
    ALLOWED_HOSTS=(list, []),
)

# Read .env file if it exists
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    environ.Env.read_env(ENV_FILE)

# -- Security (Base) --
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# -- Application Definition --
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_htmx",
]

LOCAL_APPS = [
    "core",
    "accounts",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# -- Custom User Model --
# Constitution Section 6.2: Identity Anchor
# Must be set BEFORE running migrations
AUTH_USER_MODEL = "accounts.Employee"

# -- Middleware --
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

# -- Templates --
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

# -- Database --
# PostgreSQL is the MANDATORY database engine for this project.
# SQLite is NOT supported in production or development.
# See dev.py and prod.py for environment-specific database settings.
DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# -- Password Validation --
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

# -- Internationalization --
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -- Static Files --
STATIC_URL = env("STATIC_URL", default="/static/")
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# -- Media Files --
MEDIA_URL = env("MEDIA_URL", default="/media/")
MEDIA_ROOT = BASE_DIR / "media"

# -- Default Primary Key Field Type --
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -- Custom User Model --
# Will be set in Phase 2 when Employee model is implemented
# AUTH_USER_MODEL = 'accounts.Employee'

# -- Logging --
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
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
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
    },
}

# -- Redis / Celery --
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")

# -- Celery Configuration --
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# -- HTMX --
HTMX_ENABLED = True

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-error",
}

# -- Session Settings --
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "amw_erp_session_id"
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# -- CSRF Settings --
CSRF_COOKIE_NAME = "amw_erp_csrftoken"
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = False
