"""
-- AMW Django ERP - Inventory URLs --
"""

from django.urls import path

from inventory import views

app_name = "Inventory"

urlpatterns = [
    path("products/", views.product_list, name="ProductList"),
    path("products/<slug:slug>/", views.product_detail, name="ProductDetail"),
    path("products/<slug:slug>/ledger/", views.stock_ledger, name="StockLedger"),
    path("products/<slug:slug>/adjust/", views.adjust_stock_htmx, name="AdjustStock"),
    path("categories/", views.category_list, name="CategoryList"),
    path("adjustments/", views.adjustment_list, name="AdjustmentList"),
]
