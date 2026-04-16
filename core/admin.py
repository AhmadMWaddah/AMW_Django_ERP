"""
-- AMW Django ERP - Core Admin --

Provides base admin mixins for soft delete support.
"""

from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.utils.html import format_html


class DeletedFilter(SimpleListFilter):
    """Filter to show only active, deleted, or all records."""

    title = "status"
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return [
            ("active", "Active"),
            ("deleted", "Deleted"),
            ("all", "All"),
        ]

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup,
                "query_string": cl.get_query_string({self.parameter_name: lookup}, []),
                "display": title,
            }

    def queryset(self, request, queryset):
        if self.value() == "deleted":
            return queryset.filter(deleted_at__isnull=False)
        if self.value() == "all":
            return queryset
        return queryset.filter(deleted_at__isnull=True)


class SoftDeleteAdminMixin:
    """
    Admin mixin that adds soft delete functionality.

    Features:
    - Shows all records by default (including deleted for visibility)
    - Adds "Status" filter to list view
    - Soft deletes instead of hard deletes
    - Provides restore action for deleted items
    - Shows deleted status in list view
    """

    def get_list_filter(self, request):
        list_filter = list(self.list_filter) if self.list_filter else []
        return list_filter + [DeletedFilter]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        actions["soft_delete_selected"] = self.get_action("soft_delete_selected")
        actions["restore_selected"] = self.get_action("restore_selected")
        return actions

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if hasattr(queryset, "all_with_deleted"):
            return queryset.all_with_deleted()
        return queryset

    def deleted_display(self, obj):
        if obj.is_deleted:
            return format_html('<span style="color: red;">Deleted</span>')
        return format_html('<span style="color: green;">Active</span>')

    deleted_display.short_description = "Status"

    @admin.action(description="Soft delete selected %(verbose_name_plural)s")
    def soft_delete_selected(self, request, queryset):
        """Soft delete selected objects instead of hard deleting."""
        count = queryset.filter(deleted_at__isnull=True).update(deleted_at=timezone.now())
        self.message_user(
            request,
            f"Soft deleted {count} {queryset.model._meta.verbose_name_plural}.",
            messages.SUCCESS,
        )

    @admin.action(description="Restore selected %(verbose_name_plural)s")
    def restore_selected(self, request, queryset):
        """Restore soft-deleted objects."""
        restored = queryset.filter(deleted_at__isnull=False).update(deleted_at=None)
        self.message_user(request, f"Restored {restored} {queryset.model._meta.verbose_name_plural}.", messages.SUCCESS)
