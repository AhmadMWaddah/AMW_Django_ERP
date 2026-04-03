"""
-- AMW Django ERP - Inventory URLs --
"""

from django.urls import path

from inventory import views

app_name = "Inventory"

urlpatterns = [
    path("products/", views.product_list, name="ProductList"),
    path("products/<int:product_id>/", views.product_detail, name="ProductDetail"),
    path("products/<int:product_id>/ledger/", views.stock_ledger, name="StockLedger"),
    path("products/<int:product_id>/adjust/", views.adjust_stock_htmx, name="AdjustStock"),
    path("categories/", views.category_list, name="CategoryList"),
    path("adjustments/", views.adjustment_list, name="AdjustmentList"),
]
