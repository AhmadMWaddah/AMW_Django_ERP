"""
-- AMW Django ERP - WSGI Configuration --

This module exposes the WSGI callable for production deployment.

Project: AMW Django ERP
Constitution: Constitution_AMW_DJ_ERP.md

Usage:
    gunicorn config.wsgi:application
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
