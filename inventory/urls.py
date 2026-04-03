"""
-- AMW Django ERP - Inventory URLs --
"""

from django.urls import path

from inventory import views

app_name = "inventory"

urlpatterns = [
    path("products/", views.product_list, name="product_list"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("products/<int:product_id>/ledger/", views.stock_ledger, name="stock_ledger"),
    path("products/<int:product_id>/adjust/", views.adjust_stock_htmx, name="adjust_stock"),
]
