"""
-- AMW Django ERP - Project URLs --

This is the root URL configuration for the AMW Django ERP project.

Project: AMW Django ERP
Constitution: Constitution_AMW_DJ_ERP.md
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView, TemplateView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Accounts / Authentication (with namespace)
    path("accounts/", include("accounts.urls", namespace="Accounts")),
    # Module UI (Phase 7)
    path("inventory/", include("inventory.urls")),
    path("sales/", include("sales.urls")),
    path("purchasing/", include("purchasing.urls")),
    path("security/", include("security.urls")),
    path("audit/", include("audit.urls")),
    path("reports/", include("reporting.urls", namespace="Reporting")),
    # Root redirect to dashboard
    path("", RedirectView.as_view(url="/accounts/dashboard/", permanent=False)),
    # Health Check (for monitoring)
    path("health/", TemplateView.as_view(template_name="health.html"), name="Health"),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
            *urlpatterns,
        ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = "core.views.error_403"
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"

# Note: Django does NOT support handler405 in URLconf.
# POST-only views use @require_post_with_405 decorator from core/views.py
# to render the branded 405 page on GET access.
