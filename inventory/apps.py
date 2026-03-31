from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """
    Inventory app configuration.

    Manages product catalog, stock ledger, and WAC valuation.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"
    verbose_name = "Inventory Management"
