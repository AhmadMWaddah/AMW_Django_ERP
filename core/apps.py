"""
-- AMW Django ERP - Core App Configuration --

This module configures the core application which provides:
- Shared utilities used across all apps
- Base classes for models, views, and operations
- Project-wide error handlers
- Health check endpoints
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core System"

    def ready(self):
        """
        Called when the application is loaded.
        Use this method to register signals or perform startup tasks.
        """
        # Import signals here when needed
        # from core import signals
        pass
