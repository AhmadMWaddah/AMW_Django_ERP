"""
-- AMW Django ERP - Inventory API URLs --
"""

from rest_framework import routers

from .api import CategoryViewSet, ProductViewSet

app_name = "InventoryAPI"

router = routers.DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = router.urls
