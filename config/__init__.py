# This package contains all configuration for the Django project.

from .celery import app as celery

__all__ = ("celery",)
