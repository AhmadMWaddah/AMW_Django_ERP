"""
-- AMW Django ERP - Production Settings --

This module extends base.py with production-specific configuration.
It enforces security, performance, and operational best practices.

Usage:
    export DJANGO_SETTINGS_MODULE=config.settings.prod
    gunicorn config.wsgi:application
"""

from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

# Must be explicitly set via environment variable
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be set in production")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"

# Consider adding django-csp for stricter CSP
# CSP_DEFAULT_SRC = ("'self'",)

DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
        "CONN_MAX_AGE": 600,  # Persistent connections
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@amw-erp.com")

LOGGING["handlers"]["file"] = {
    "class": "logging.FileHandler",
    "filename": BASE_DIR / "logs" / "django-prod.log",
    "formatter": "verbose",
}
LOGGING["root"]["handlers"] = ["console", "file"]
LOGGING["root"]["level"] = "WARNING"
LOGGING["loggers"]["django"]["level"] = "INFO"

CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_CONCURRENCY = 4

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# For now, using local storage. Consider migrating to cloud storage.
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Add rate limiting for authentication and API endpoints

# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
# sentry_sdk.init(
#     dsn=env('SENTRY_DSN'),
#     integrations=[DjangoIntegration()],
#     traces_sample_rate=0.1,
# )

# Run: python manage.py check --deploy
# This will verify production security settings
