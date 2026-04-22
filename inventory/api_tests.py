"""
-- AMW Django ERP - Inventory API Tests --

Constitution Section 13: Testing & Verification Law
- API endpoints require tests for CRUD operations
- Tests validate serializer behavior and view permissions
"""

from decimal import Decimal

import pytest
from django.test import Client
from rest_framework import status

from accounts.models import Employee
from inventory.models import Category, Product


@pytest.fixture
def api_client():
    return Client()


@pytest.fixture
def authenticated_employee(db):
    employee = Employee.objects.create_user(
        email="api-test@amw.io", password="test123", first_name="API", last_name="Tester"
    )
    return employee


@pytest.fixture
def authenticated_client(api_client, authenticated_employee):
    api_client.force_login(authenticated_employee)
    api_client.defaults["HTTP_ACCEPT"] = "application/json"
    return api_client


@pytest.fixture
def category():
    return Category.objects.create(name="Test Category", description="Test Description")


@pytest.fixture
def subcategory(category):
    return Category.objects.create(name="Sub Category", parent=category, description="Sub Description")


@pytest.fixture
def product(category):
    return Product.objects.create(
        sku="API-TEST-001",
        name="Test Product",
        category=category,
        current_stock=Decimal("10.0000"),
        wac_price=Decimal("50.0000"),
    )


@pytest.mark.django_db
class TestCategoryAPI:
    def test_list_categories(self, authenticated_client, category):
        response = authenticated_client.get("/api/v1/categories/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert len(data["results"]) >= 1
        assert data["results"][0]["name"] == "Test Category"

    def test_create_category(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/categories/", {"name": "New Category", "description": "New Description"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name="New Category").exists()

    def test_retrieve_category(self, authenticated_client, category):
        response = authenticated_client.get(f"/api/v1/categories/{category.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Test Category"

    def test_update_category(self, authenticated_client, category):
        response = authenticated_client.patch(
            f"/api/v1/categories/{category.id}/",
            {"description": "Updated Description"},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.description == "Updated Description"

    def test_delete_category(self, authenticated_client, category):
        response = authenticated_client.delete(f"/api/v1/categories/{category.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        category.refresh_from_db()
        assert category.is_deleted is True

    def test_category_include_deleted(self, authenticated_client, category):
        cat_id = category.id
        category.delete()
        response = authenticated_client.get("/api/v1/categories/?include_deleted=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any(c["id"] == cat_id for c in data["results"])

    def test_category_include_deleted_false(self, authenticated_client, category):
        cat_id = category.id
        category.delete()
        response = authenticated_client.get("/api/v1/categories/?include_deleted=false")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert not any(c["id"] == cat_id for c in data["results"])

    def test_category_search(self, authenticated_client, category):
        response = authenticated_client.get("/api/v1/categories/?search=Test")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) >= 1


@pytest.mark.django_db
class TestProductAPI:
    def test_list_products(self, authenticated_client, product):
        response = authenticated_client.get("/api/v1/products/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert len(data["results"]) >= 1

    def test_create_product(self, authenticated_client, category):
        response = authenticated_client.post(
            "/api/v1/products/",
            {
                "sku": "api-new-001",
                "name": "New Product",
                "category_id": category.id,
                "unit_of_measure": "pcs",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(sku="API-NEW-001").exists()

    def test_sku_uppercase_conversion(self, authenticated_client, category):
        response = authenticated_client.post(
            "/api/v1/products/",
            {
                "sku": "lowercase-sku",
                "name": "Lowercase SKU Product",
                "category_id": category.id,
                "unit_of_measure": "pcs",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        product = Product.objects.get(name="Lowercase SKU Product")
        assert product.sku == "LOWERCASE-SKU"

    def test_retrieve_product(self, authenticated_client, product):
        response = authenticated_client.get(f"/api/v1/products/{product.id}/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sku"] == "API-TEST-001"
        assert Decimal(data["stock_value"]) == Decimal("500.0000")

    def test_update_product(self, authenticated_client, product):
        response = authenticated_client.patch(
            f"/api/v1/products/{product.id}/",
            {"name": "Updated Product"},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.name == "Updated Product"

    def test_delete_product(self, authenticated_client, product):
        response = authenticated_client.delete(f"/api/v1/products/{product.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        product.refresh_from_db()
        assert product.is_deleted is True

    def test_product_include_deleted(self, authenticated_client, product):
        prod_id = product.id
        product.delete()
        response = authenticated_client.get("/api/v1/products/?include_deleted=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any(p["id"] == prod_id for p in data["results"])

    def test_product_filter_by_category(self, authenticated_client, product, category):
        response = authenticated_client.get(f"/api/v1/products/?category={category.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) >= 1

    def test_product_search(self, authenticated_client, product):
        response = authenticated_client.get("/api/v1/products/?search=API-TEST")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) >= 1


@pytest.mark.django_db
class TestProductStockValue:
    def test_stock_value_endpoint(self, authenticated_client, product):
        response = authenticated_client.get(f"/api/v1/products/{product.id}/stock-value/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sku"] == "API-TEST-001"
        assert Decimal(data["stock_value"]) == Decimal("500.0000")


@pytest.mark.django_db
class TestProductStockBulk:
    def test_stock_endpoint_all(self, authenticated_client, product):
        response = authenticated_client.get("/api/v1/products/stock/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_stock_endpoint_filter_out_of_stock(self, authenticated_client, product, category):
        Product.objects.filter(pk=product.pk).update(current_stock=Decimal("0.0000"))
        response = authenticated_client.get("/api/v1/products/stock/?stock_status=out_of_stock")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(p["current_stock"] == "0.0000" for p in data)

    def test_stock_endpoint_filter_in_stock(self, authenticated_client, product):
        response = authenticated_client.get("/api/v1/products/stock/?stock_status=in_stock")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(Decimal(p["current_stock"]) > 10 for p in data)


@pytest.mark.django_db
class TestAPIUnauthenticated:
    def test_unauthenticated_access_denied(self, api_client):
        response = api_client.get("/api/v1/products/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCategoryOrdering:
    def test_category_ordering_asc(self, authenticated_client, category):
        response = authenticated_client.get("/api/v1/categories/?ordering=name")
        assert response.status_code == status.HTTP_200_OK

    def test_category_ordering_desc(self, authenticated_client, category):
        response = authenticated_client.get("/api/v1/categories/?ordering=-name")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProductOrdering:
    def test_product_ordering_by_sku(self, authenticated_client, product):
        response = authenticated_client.get("/api/v1/products/?ordering=sku")
        assert response.status_code == status.HTTP_200_OK

    def test_product_ordering_by_name(self, authenticated_client, product):
        response = authenticated_client.get("/api/v1/products/?ordering=name")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPagination:
    def test_pagination_default_10(self, authenticated_client, category):
        for i in range(15):
            Category.objects.create(name=f"Category {i}", description=f"Desc {i}")
        response = authenticated_client.get("/api/v1/categories/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert len(data["results"]) <= 10


@pytest.mark.django_db
class TestEdgeCases:
    def test_list_empty_products(self, authenticated_client):
        Product.objects.all().delete()
        response = authenticated_client.get("/api/v1/products/")
        assert response.status_code == status.HTTP_200_OK

    def test_list_empty_categories(self, authenticated_client):
        Category.objects.all().delete()
        response = authenticated_client.get("/api/v1/categories/")
        assert response.status_code == status.HTTP_200_OK

    def test_product_invalid_category(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/products/",
            {
                "sku": "test-invalid",
                "name": "Test Invalid",
                "category_id": 99999,
                "unit_of_measure": "pcs",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_product_search_no_results(self, authenticated_client, product):
        response = authenticated_client.get("/api/v1/products/?search=NONEXISTENT")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 0
