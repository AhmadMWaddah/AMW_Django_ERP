"""
-- AMW Django ERP - Security URLs --
Phase 7.5: Added detail view URLs.
"""

from django.urls import path

from security import views

app_name = "Security"

urlpatterns = [
    path("departments/", views.department_list, name="DepartmentList"),
    path("departments/<slug:slug>/", views.department_detail, name="DepartmentDetail"),
    path("roles/", views.role_list, name="RoleList"),
    path("roles/<slug:slug>/", views.role_detail, name="RoleDetail"),
    path("policies/", views.policy_list, name="PolicyList"),
    path("policies/<slug:slug>/", views.policy_detail, name="PolicyDetail"),
]
