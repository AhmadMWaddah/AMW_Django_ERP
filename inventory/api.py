from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        include_deleted = self.request.query_params.get("include_deleted")
        if include_deleted and include_deleted.lower() == "true":
            queryset = Category.objects.all_with_deleted()
        else:
            queryset = queryset.filter(deleted_at__isnull=True)
        return queryset


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["sku", "name", "description"]
    ordering_fields = ["sku", "name", "current_stock", "created_at"]
    ordering = ["sku"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("category")
        include_deleted = self.request.query_params.get("include_deleted")
        if include_deleted and include_deleted.lower() == "true":
            queryset = Product.objects.all_with_deleted()
        else:
            queryset = queryset.filter(deleted_at__isnull=True)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    def perform_destroy(self, instance):
        instance.delete()  # Soft delete via SoftDeleteModel

    @action(detail=True, methods=["get"], url_path="stock-value")
    def stock_value(self, request, pk=None):
        product = self.get_object()
        return Response(
            {
                "sku": product.sku,
                "name": product.name,
                "current_stock": product.current_stock,
                "wac_price": product.wac_price,
                "stock_value": product.get_stock_value(),
            }
        )

    @action(detail=False, methods=["get"])
    def stock(self, request):
        queryset = self.get_queryset()
        stock_status = request.query_params.get("stock_status")
        if stock_status == "out_of_stock":
            queryset = queryset.filter(current_stock=0)
        elif stock_status == "low_stock":
            queryset = queryset.filter(current_stock__gt=0, current_stock__lte=10)
        elif stock_status == "in_stock":
            queryset = queryset.filter(current_stock__gt=10)
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)
