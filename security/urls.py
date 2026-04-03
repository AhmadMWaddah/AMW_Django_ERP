"""
-- AMW Django ERP - Security URLs --
"""

from django.urls import path

from security import views

app_name = "Security"

urlpatterns = [
    path("departments/", views.department_list, name="DepartmentList"),
    path("roles/", views.role_list, name="RoleList"),
    path("policies/", views.policy_list, name="PolicyList"),
]
