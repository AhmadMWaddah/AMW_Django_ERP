"""
-- AMW Django ERP - Purchasing URLs --
"""

from django.urls import path

from purchasing import views

app_name = "purchasing"

urlpatterns = [
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/<int:supplier_id>/", views.supplier_detail, name="supplier_detail"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<int:order_id>/receive/", views.receive_stock_htmx, name="receive_stock"),
]
