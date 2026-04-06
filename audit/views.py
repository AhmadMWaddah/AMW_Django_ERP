"""Audit log views with list, detail, search, and pagination."""

from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, render

from audit.models import AuditLog
from core.utils import paginate_queryset


@login_required
def audit_log_list(request):
    """Audit log list view with search and pagination."""
    query = request.GET.get("q", "").strip()
    action_filter = request.GET.get("action", "").strip()

    logs = AuditLog.objects.select_related("actor").order_by("-timestamp")

    if query:
        logs = logs.filter(
            models.Q(actor_name__icontains=query)
            | models.Q(actor_email__icontains=query)
            | models.Q(action_code__icontains=query)
            | models.Q(object_repr__icontains=query)
            | models.Q(content_type__icontains=query)
        )

    if action_filter:
        logs = logs.filter(action=action_filter)

    pagination_data = paginate_queryset(logs, request)

    context = {
        "query": query,
        "action_filter": action_filter,
        "logs": pagination_data["page_obj"].object_list,
        "title": "Audit Logs",
        "row_template": "audit/components/audit_log_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(request, "audit/pages/audit_log_list.html", context)


@login_required
def audit_log_detail(request, pk):
    """Audit log detail view with before/after data display."""
    log = get_object_or_404(AuditLog, pk=pk)

    context = {
        "log": log,
    }

    return render(request, "audit/pages/audit_log_detail.html", context)
