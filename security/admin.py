"""
-- AMW Django ERP - Security/IAM Admin --

Registers security models in Django admin for IAM management.
"""

from django.contrib import admin

from security.models import Department, Policy, Role


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin interface for Department model."""

    list_display = ["name", "code", "parent", "is_active", "created_at"]
    list_filter = ["parent", "is_active"]
    search_fields = ["name", "code", "description"]
    ordering = ["name"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Department Details", {"fields": ("name", "code", "parent", "description")}),
        ("Status", {"fields": ("is_active", "created_at", "updated_at")}),
    )


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    """Admin interface for Policy model."""

    list_display = ["name", "code", "resource", "action", "effect", "is_active"]
    list_filter = ["effect", "is_active", "resource"]
    search_fields = ["name", "code", "description", "resource", "action"]
    ordering = ["name"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Policy Details",
            {
                "fields": (
                    "name",
                    "code",
                    "description",
                    "resource",
                    "action",
                    "effect",
                )
            },
        ),
        ("Status", {"fields": ("is_active", "created_at", "updated_at")}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role model."""

    list_display = ["name", "department", "is_active", "created_at"]
    list_filter = ["department", "is_active"]
    search_fields = ["name", "code", "description"]
    ordering = ["department__name", "name"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["policies"]

    fieldsets = (
        ("Role Details", {"fields": ("name", "code", "department", "description")}),
        ("Policies", {"fields": ("policies",)}),
        ("Status", {"fields": ("is_active", "created_at", "updated_at")}),
    )
