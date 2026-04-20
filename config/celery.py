"""
-- AMW Django ERP - Celery Configuration --

This module configures Celery for asynchronous task processing.

Project: AMW Django ERP
Constitution: Constitution_AMW_DJ_ERP.md

Usage:
    celery -A config worker --loglevel=info
    celery -A config beat --loglevel=info
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

celery = Celery("amw_django_erp")

celery.config_from_object("django.conf:settings", namespace="CELERY")

celery.autodiscover_tasks()


@celery.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
