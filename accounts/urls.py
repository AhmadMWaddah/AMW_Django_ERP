"""
-- AMW Django ERP - Accounts URLs --

Authentication URL patterns: login, logout, dashboard
"""

# -- Standard Library --

# -- Third-Party (Django) --
from django.urls import path

# -- Local Imports --
from . import views

app_name = "Accounts"

urlpatterns = [
    path("login/", views.login_view, name="Login"),
    path("logout/", views.logout_view, name="Logout"),
    path("dashboard/", views.dashboard_view, name="Dashboard"),
]
