"""
-- AMW Django ERP - Audit Admin --

Registers audit models in Django admin for compliance and traceability.
"""

from django.contrib import admin

from audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model."""

    list_display = ["timestamp", "actor", "action", "action_code", "content_type", "object_id"]
    list_filter = ["action", "content_type", "timestamp"]
    search_fields = ["actor_email", "actor_name", "action_code", "object_repr"]
    ordering = ["-timestamp"]
    readonly_fields = [
        "actor",
        "actor_email",
        "actor_name",
        "action",
        "action_code",
        "action_description",
        "content_type",
        "object_id",
        "object_repr",
        "before_data",
        "after_data",
        "timestamp",
        "ip_address",
        "user_agent",
        "extra_data",
    ]

    fieldsets = (
        ("Actor Information", {"fields": ("actor", "actor_email", "actor_name")}),
        ("Action Information", {"fields": ("action", "action_code", "action_description")}),
        ("Target Information", {"fields": ("content_type", "object_id", "object_repr")}),
        ("State Changes", {"fields": ("before_data", "after_data")}),
        ("Metadata", {"fields": ("timestamp", "ip_address", "user_agent", "extra_data")}),
    )

    def has_add_permission(self, request):
        # Prevent manual creation - audit logs are created automatically
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent modification - audit logs are immutable
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion - audit logs must be preserved
        return False
