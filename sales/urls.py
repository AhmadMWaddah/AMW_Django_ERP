"""
-- AMW Django ERP - Sales URLs --
"""

from django.urls import path

from sales import views

app_name = "sales"

urlpatterns = [
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/<int:customer_id>/", views.customer_detail, name="customer_detail"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<int:order_id>/confirm/", views.confirm_order_htmx, name="confirm_order"),
    path("orders/<int:order_id>/void/", views.void_order_htmx, name="void_order"),
]
