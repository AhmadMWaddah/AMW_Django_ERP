"""
-- AMW Django ERP - Development Settings --

This module extends base.py with development-specific configuration.
It enables debug tools, verbose logging, and relaxed security for local development.

Usage:
    export DJANGO_SETTINGS_MODULE=config.settings.dev
    python manage.py runserver 8010
"""

from importlib.util import find_spec

from .base import *

# -- Debug Mode --
DEBUG = True

# -- Allowed Hosts (Development) --
ALLOWED_HOSTS += ["localhost", "127.0.0.1"]

# -- Database (PostgreSQL for Development) --
DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": env("DB_NAME", default="amw_django_erp"),
        "USER": env("DB_USER", default="amw_erp_user"),
        "PASSWORD": env("DB_PASSWORD", default="amw_erp_password_dev"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

# -- Django Debug Toolbar --
if find_spec("debug_toolbar"):
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INTERNAL_IPS = ["127.0.0.1"]

# -- Development Email Backend --
# Emails are printed to console instead of being sent
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# -- Logging (Verbose for Development) --
LOGGING["root"]["level"] = "DEBUG"
LOGGING["loggers"]["django"]["level"] = "DEBUG"

# -- Show All SQL Queries (Development Only) --
# LOGGING['loggers']['django.db.backends'] = {
#     'level': 'DEBUG',
#     'handlers': ['console'],
# }

# -- Celery (Development) --
# Run tasks synchronously for easier debugging
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# -- Cache (Development - Simple Memory Cache) --
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# -- Security Warnings --
# These are intentionally relaxed for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
X_FRAME_OPTIONS = "SAMEORIGIN"

# -- Django Extensions (Optional Development Tools) --
if find_spec("django_extensions"):
    INSTALLED_APPS += ["django_extensions"]

# -- Development Server Port --
# Default port for this project is 8010 (not 8000)
# Run: python manage.py runserver 8010
