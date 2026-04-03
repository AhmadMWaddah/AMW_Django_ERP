"""
-- AMW Django ERP - Accounts URLs --

Authentication URL patterns: login, logout, dashboard
"""

from django.urls import path

from . import views

app_name = "Accounts"

urlpatterns = [
    path("login/", views.login_view, name="Login"),
    path("logout/", views.logout_view, name="Logout"),
    path("dashboard/", views.dashboard_view, name="Dashboard"),
    path("employees/", views.employee_list, name="EmployeeList"),
]
