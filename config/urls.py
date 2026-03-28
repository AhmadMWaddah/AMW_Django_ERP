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
from django.views.generic.base import TemplateView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Health Check (for monitoring)
    path("health/", TemplateView.as_view(template_name="health.html"), name="health"),
    # Core URLs will be added as apps are developed
    # path('', include('core.urls')),
    # path('accounts/', include('accounts.urls')),
    # path('inventory/', include('inventory.urls')),
    # path('sales/', include('sales.urls')),
    # path('purchasing/', include('purchasing.urls')),
]

# -- Static & Media Files (Development) --
if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
            *urlpatterns,
        ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# -- Error Pages --
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"
