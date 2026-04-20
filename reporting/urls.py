"""
-- AMW Django ERP - Reporting URLs --

URL configuration for reporting module.

Constitution Alignment:
- Section 15.8: Reporting must align with Architecture targets
"""

from django.urls import path

from . import views

app_name = "reporting"

urlpatterns = [
    path("", views.report_list, name="list"),
    path("request/", views.request_report, name="request"),
]
