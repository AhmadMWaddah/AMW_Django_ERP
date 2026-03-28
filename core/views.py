"""
-- AMW Django ERP - Core Views --

This module contains core views including error handlers and health checks.
"""

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
