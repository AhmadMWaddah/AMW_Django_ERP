"""
-- AMW Django ERP - ASGI Configuration --

This module exposes the ASGI callable for async-capable servers.

Project: AMW Django ERP
Constitution: Constitution_AMW_DJ_ERP.md

Usage:
    uvicorn config.asgi:application
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_asgi_application()
