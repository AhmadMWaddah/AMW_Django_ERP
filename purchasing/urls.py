"""
-- AMW Django ERP - Purchasing URLs --
"""

from django.urls import path

from purchasing import views

app_name = "Purchasing"

urlpatterns = [
    path("suppliers/", views.supplier_list, name="SupplierList"),
    path("suppliers/<int:supplier_id>/", views.supplier_detail, name="SupplierDetail"),
    path("orders/", views.order_list, name="OrderList"),
    path("orders/<int:order_id>/", views.order_detail, name="OrderDetail"),
    path("orders/<int:order_id>/receive/", views.receive_stock_htmx, name="ReceiveStock"),
]
