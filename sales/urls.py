"""
-- AMW Django ERP - Sales URLs --
"""

from django.urls import path

from sales import views

app_name = "Sales"

urlpatterns = [
    path("customers/", views.customer_list, name="CustomerList"),
    path("customers/<slug:slug>/", views.customer_detail, name="CustomerDetail"),
    path("customers/<slug:customer_slug>/create-order/", views.order_create, name="CreateOrder"),
    path("orders/", views.order_list, name="OrderList"),
    path("orders/<int:order_id>/", views.order_detail, name="OrderDetail"),
    path("orders/<int:order_id>/confirm/", views.confirm_order_htmx, name="ConfirmOrder"),
    path("orders/<int:order_id>/void/", views.void_order_htmx, name="VoidOrder"),
]
