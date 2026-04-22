from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    full_path = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "parent_name",
            "description",
            "full_path",
            "created_at",
            "modified_at",
            "deleted_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "modified_at", "deleted_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["is_deleted"] = instance.deleted_at is not None
        return representation


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    stock_value = serializers.DecimalField(
        source="get_stock_value",
        max_digits=19,
        decimal_places=4,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "slug",
            "name",
            "category",
            "category_name",
            "current_stock",
            "wac_price",
            "stock_value",
            "unit_of_measure",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "current_stock",
            "wac_price",
            "deleted_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["is_deleted"] = instance.deleted_at is not None
        return representation


class ProductDetailSerializer(ProductListSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta(ProductListSerializer.Meta):
        fields = [
            "id",
            "sku",
            "slug",
            "name",
            "category",
            "category_id",
            "category_name",
            "description",
            "location_note",
            "unit_of_measure",
            "current_stock",
            "wac_price",
            "stock_value",
            "created_at",
            "modified_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "current_stock",
            "wac_price",
            "created_at",
            "modified_at",
            "deleted_at",
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
    )

    class Meta:
        model = Product
        fields = [
            "sku",
            "name",
            "category_id",
            "description",
            "location_note",
            "unit_of_measure",
        ]

    def validate_sku(self, value):
        return value.upper()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if "sku" in attrs:
            attrs["sku"] = attrs["sku"].upper()
        return attrs
