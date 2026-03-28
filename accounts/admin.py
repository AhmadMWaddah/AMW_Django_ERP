"""
-- AMW Django ERP - Employee Admin Configuration --

Provides admin interface for Employee model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(BaseUserAdmin):
    """
    Admin configuration for Employee model.
    Extends Django's BaseUserAdmin for email-based authentication.
    """

    # -- List Display --
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "date_joined")

    # -- Search --
    search_fields = ("email", "first_name", "last_name")

    # -- Ordering --
    ordering = ("email",)

    # -- Fieldsets --
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important Dates"), {"fields": ("date_joined",)}),
    )

    # -- Add User Form --
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    # -- Read-only Fields --
    readonly_fields = ("date_joined",)

    # -- Filter Horizontal --
    filter_horizontal = ("groups", "user_permissions")
