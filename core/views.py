"""
-- AMW Django ERP - Core Views --

This module contains core views including error handlers and health checks.
"""

from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render


def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        JSON response with service status
    """
    return JsonResponse({"status": "healthy", "service": "AMW Django ERP"})


def error_404(request, exception):
    """
    Custom 404 error handler.
    Constitution: Provide user-friendly error pages.
    """
    return render(request, "core/errors/404.html", status=404)


def error_500(request):
    """
    Custom 500 error handler.
    Constitution: Log errors and show user-friendly message.
    """
    return render(request, "core/errors/500.html", status=500)


def error_403(request, exception):
    """
    Custom 403 error handler.
    Constitution: Provide user-friendly error pages for permission denied.
    """
    return render(request, "core/errors/403.html", {"exception": exception}, status=403)


def error_405(request, exception=None):
    """
    Custom 405 error handler - renders branded Method Not Allowed page.
    Constitution: Provide user-friendly error pages for method not allowed.

    Note: Django does NOT support handler405 in URLconf, so this must be
    called explicitly from views that need 405 handling.
    """
    return render(request, "core/errors/405.html", {"exception": exception or "Method Not Allowed"}, status=405)


def require_post_with_405(view_func):
    """
    Decorator that enforces POST-only access and renders branded 405 page on GET.

    Unlike @require_POST which returns plain-text HttpResponseNotAllowed,
    this decorator renders our custom 405 template.

    For HTMX requests (hx-* headers), returns JSON 405 with HX-Trigger for toast.
    For regular GET requests, renders the branded 405 page.

    Usage:
        @require_post_with_405
        @login_required
        def my_post_only_view(request, order_id):
            # Only POST requests reach here
            pass
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method != "POST":
            # Check if this is an HTMX request
            if getattr(request, "htmx", False):
                return JsonResponse(
                    {"error": "Method Not Allowed. This endpoint requires a POST request."},
                    status=405,
                    headers={
                        "HX-Trigger": '{"showToast": {"message": "Method Not Allowed. Use POST request.", "type": "error"}}',
                    },
                )
            # Regular GET request - render branded 405 page
            return error_405(request, exception="This action requires a POST request.")

        return view_func(request, *args, **kwargs)

    return wrapper
