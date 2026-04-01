from django.apps import AppConfig


class SalesConfig(AppConfig):
    """
    Sales app configuration.

    Manages CRM, sales orders, and order fulfillment operations.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "sales"
    verbose_name = "Sales & CRM"
