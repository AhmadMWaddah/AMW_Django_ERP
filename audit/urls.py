"""Audit log URL configuration."""

from django.urls import path

from audit import views

app_name = "audit"

urlpatterns = [
    path("", views.audit_log_list, name="AuditLogList"),
    path("<int:pk>/", views.audit_log_detail, name="AuditLogDetail"),
]
