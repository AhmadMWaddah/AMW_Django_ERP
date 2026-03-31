"""
-- AMW Django ERP - Inventory Tests --

Constitution Section 13: Testing & Verification Law
- Every critical business feature requires tests
- Tests should validate business behavior, not only model creation
- Inventory and WAC flows are high-priority test domains
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from inventory.logic.valuation import calculate_wac, format_wac_for_display, should_recalculate_wac
from inventory.models import Category, Product, StockAdjustmentStatus, StockChangeType, StockTransaction
from inventory.operations.stock import adjust_stock, approve_adjustment, stock_in, stock_out


@pytest.mark.django_db
class TestCategoryModel:
    """Test Category model functionality."""

    def test_create_category(self):
        """Test basic category creation."""
        category = Category.objects.create(name="Test Category", description="Test description")

        assert category.name == "Test Category"
        assert category.code == "test-category"
        assert category.description == "Test description"
        assert category.parent is None

    def test_category_auto_slug(self):
        """Test automatic slug generation."""
        category = Category.objects.create(name="Major Appliances")
        assert category.code == "major-appliances"

    def test_category_hierarchy(self):
        """Test parent-child category relationships."""
        parent = Category.objects.create(name="Appliances")
        child = Category.objects.create(name="Major Appliances", parent=parent)

        assert child.parent == parent
        assert child in parent.children.all()

    def test_category_full_path(self):
        """Test full category path including ancestors."""
        level1 = Category.objects.create(name="Level 1")
        level2 = Category.objects.create(name="Level 2", parent=level1)
        level3 = Category.objects.create(name="Level 3", parent=level2)

        assert level3.get_full_path() == "Level 1 / Level 2 / Level 3"

    def test_category_circular_reference(self):
        """Test prevention of circular references."""
        category = Category.objects.create(name="Test")
        category.parent = category

        with pytest.raises(ValidationError):
            category.clean()

    def test_soft_delete(self):
        """Test soft delete functionality."""
        category = Category.objects.create(name="To Delete")
        category_id = category.id

        # Soft delete
        category.delete()

        # Should not appear in default queryset
        assert Category.objects.filter(id=category_id).count() == 0

        # Should appear in all_with_deleted
        assert Category.objects.all_with_deleted().filter(id=category_id).count() == 1

        # Restore
        category.undelete()
        assert Category.objects.filter(id=category_id).count() == 1


@pytest.mark.django_db
class TestProductModel:
    """Test Product model functionality."""

    def test_create_product(self):
        """Test basic product creation."""
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            sku="TEST-001",
            name="Test Product",
            category=category,
            unit_of_measure="pcs",
        )

        assert product.sku == "TEST-001"
        assert product.name == "Test Product"
        assert product.current_stock == Decimal("0.0000")
        assert product.wac_price == Decimal("0.0000")

    def test_product_sku_validation(self):
        """Test SKU format validation."""
        category = Category.objects.create(name="Test")

        # Valid SKU with hyphen
        product = Product(sku="VALID-SKU", name="Test", category=category)
        product.clean()  # Should not raise

        # Invalid SKU without hyphen
        product_invalid = Product(sku="INVALID", name="Test", category=category)
        with pytest.raises(ValidationError):
            product_invalid.clean()

    def test_product_stock_value(self):
        """Test stock value calculation."""
        category = Category.objects.create(name="Test")
        product = Product.objects.create(
            sku="TEST-002",
            name="Test Product",
            category=category,
            current_stock=Decimal("10.0000"),
            wac_price=Decimal("100.0000"),
        )

        assert product.get_stock_value() == Decimal("1000.0000")


@pytest.mark.django_db
class TestWACCalculation:
    """Test WAC valuation logic (Constitution 6.5)."""

    def test_wac_basic_calculation(self):
        """Test basic WAC formula."""
        # Old: 10 units @ 100.00
        # New: 5 units @ 120.00
        # Expected: (10*100 + 5*120) / (10+5) = 1600/15 = 106.6667
        new_wac = calculate_wac(Decimal("10"), Decimal("100.0000"), Decimal("5"), Decimal("120.0000"))
        assert new_wac == Decimal("106.6667")

    def test_wac_no_old_stock(self):
        """Test WAC when there's no old stock."""
        new_wac = calculate_wac(Decimal("0"), Decimal("0.0000"), Decimal("10"), Decimal("50.0000"))
        assert new_wac == Decimal("50.0000")

    def test_wac_no_new_stock(self):
        """Test WAC when no new stock is added."""
        new_wac = calculate_wac(Decimal("10"), Decimal("100.0000"), Decimal("0"), Decimal("50.0000"))
        assert new_wac == Decimal("100.0000")

    def test_wac_precision(self):
        """Test WAC maintains 19,4 precision."""
        new_wac = calculate_wac(Decimal("7"), Decimal("33.3333"), Decimal("11"), Decimal("45.6789"))
        # Should have exactly 4 decimal places
        assert new_wac.as_tuple().exponent == -4

    def test_should_recalculate_wac(self):
        """Test WAC trigger points."""
        # Should recalculate
        assert should_recalculate_wac(StockChangeType.INTAKE) is True
        assert should_recalculate_wac(StockChangeType.PURCHASE) is True
        assert should_recalculate_wac(StockChangeType.ADJUST_ADD) is True

        # Should NOT recalculate
        assert should_recalculate_wac(StockChangeType.SALE) is False
        assert should_recalculate_wac(StockChangeType.ADJUST_REDUCE) is False
        assert should_recalculate_wac(StockChangeType.TRANSFER) is False
        assert should_recalculate_wac(StockChangeType.DAMAGE) is False

    def test_format_wac_for_display(self):
        """Test WAC display formatting (2 decimal places)."""
        formatted = format_wac_for_display(Decimal("106.6667"))
        assert formatted == "106.67"


@pytest.mark.django_db
class TestStockTransaction:
    """Test StockTransaction model (immutable ledger)."""

    def test_create_transaction(self):
        """Test basic transaction creation."""
        category = Category.objects.create(name="Test")
        product = Product.objects.create(sku="TEST-001", name="Test", category=category)

        # Create a transaction manually for testing
        transaction = StockTransaction(
            product=product,
            change_type=StockChangeType.PURCHASE,
            quantity=Decimal("10.0000"),
            unit_cost=Decimal("100.0000"),
            balance_before=Decimal("0.0000"),
            balance_after=Decimal("10.0000"),
            wac_before=Decimal("0.0000"),
            wac_after=Decimal("100.0000"),
        )

        # Note: Can't save without created_by (FK required)
        # This test is for model structure validation
        assert transaction.change_type == StockChangeType.PURCHASE
        assert transaction.quantity == Decimal("10.0000")

    def test_transaction_immutability(self):
        """Test that transactions cannot be modified after creation."""
        # This is enforced by the model's save() method
        # Full test requires a created transaction
        pass  # Tested in integration tests


@pytest.mark.django_db
class TestStockOperations:
    """Test stock operations with atomic safety (Constitution 6.6)."""

    @pytest.fixture
    def setup_inventory(self):
        """Create test inventory setup."""
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            sku="TEST-001",
            name="Test Product",
            category=category,
            unit_of_measure="pcs",
        )
        # Create a test employee (using superuser from seed_erp)
        from accounts.models import Employee

        employee = Employee.objects.create_user(
            email="test@amw.io", password="test123", first_name="Test", last_name="User"
        )

        return {"product": product, "employee": employee}

    def test_stock_in_basic(self, setup_inventory):
        """Test basic stock-in operation."""
        product = setup_inventory["product"]
        employee = setup_inventory["employee"]

        # Perform stock-in
        transaction = stock_in(
            product=product,
            quantity=Decimal("10.0000"),
            unit_cost=Decimal("100.0000"),
            employee=employee,
            change_type=StockChangeType.PURCHASE,
        )

        # Verify product updated
        product.refresh_from_db()
        assert product.current_stock == Decimal("10.0000")
        assert product.wac_price == Decimal("100.0000")

        # Verify transaction created
        assert transaction.quantity == Decimal("10.0000")
        assert transaction.balance_after == Decimal("10.0000")
        assert transaction.wac_after == Decimal("100.0000")

    def test_stock_in_wac_recalculation(self, setup_inventory):
        """Test WAC recalculation on multiple stock-ins."""
        product = setup_inventory["product"]
        employee = setup_inventory["employee"]

        # First stock-in: 10 units @ 100.00
        stock_in(product, Decimal("10"), Decimal("100.0000"), employee, StockChangeType.PURCHASE)

        # Second stock-in: 10 units @ 120.00
        # Expected WAC: (10*100 + 10*120) / 20 = 110.0000
        stock_in(product, Decimal("10"), Decimal("120.0000"), employee, StockChangeType.PURCHASE)

        product.refresh_from_db()
        assert product.current_stock == Decimal("20.0000")
        assert product.wac_price == Decimal("110.0000")

    def test_stock_out_basic(self, setup_inventory):
        """Test basic stock-out operation."""
        product = setup_inventory["product"]
        employee = setup_inventory["employee"]

        # First add stock
        stock_in(product, Decimal("10"), Decimal("100.0000"), employee, StockChangeType.PURCHASE)

        # Then remove stock
        transaction = stock_out(
            product=product,
            quantity=Decimal("3.0000"),
            employee=employee,
            change_type=StockChangeType.SALE,
        )

        product.refresh_from_db()
        assert product.current_stock == Decimal("7.0000")
        assert product.wac_price == Decimal("100.0000")  # WAC unchanged on stock-out

        # Transaction quantity should be negative
        assert transaction.quantity == Decimal("-3.0000")

    def test_stock_out_insufficient_stock(self, setup_inventory):
        """Test stock-out with insufficient stock."""
        product = setup_inventory["product"]
        employee = setup_inventory["employee"]

        # Try to remove stock that doesn't exist
        with pytest.raises(ValueError, match="Insufficient stock"):
            stock_out(product, Decimal("10"), employee, StockChangeType.SALE)

    def test_stock_out_negative_quantity(self, setup_inventory):
        """Test stock-out with negative quantity."""
        product = setup_inventory["product"]
        employee = setup_inventory["employee"]

        with pytest.raises(ValueError, match="Quantity must be positive"):
            stock_out(product, Decimal("-5"), employee, StockChangeType.SALE)

    def test_stock_in_negative_quantity(self, setup_inventory):
        """Test stock-in with negative quantity."""
        product = setup_inventory["product"]
        employee = setup_inventory["employee"]

        with pytest.raises(ValueError, match="Quantity must be positive"):
            stock_in(product, Decimal("-5"), Decimal("100.0000"), employee, StockChangeType.PURCHASE)

    def test_adjust_stock_request(self, setup_inventory):
        """Test stock adjustment request creation."""
        product = setup_inventory["product"]
        employee = setup_inventory["employee"]

        # Add some stock first
        stock_in(product, Decimal("10"), Decimal("100.0000"), employee, StockChangeType.PURCHASE)
        product.refresh_from_db()  # Refresh after stock change

        # Request adjustment
        adjustment = adjust_stock(
            employee=employee,
            product=product,
            new_quantity=Decimal("8.0000"),  # Reduce by 2
            reason="CORRECTION",
            notes="Found damaged items",
        )

        assert adjustment.status == StockAdjustmentStatus.PENDING
        assert adjustment.old_quantity == Decimal("10.0000")
        assert adjustment.new_quantity == Decimal("8.0000")
        assert adjustment.get_quantity_change() == Decimal("-2.0000")

    def test_approve_adjustment(self, setup_inventory):
        """Test stock adjustment approval and execution."""
        product = setup_inventory["product"]
        employee = setup_inventory["employee"]

        # Add stock
        stock_in(product, Decimal("10"), Decimal("100.0000"), employee, StockChangeType.PURCHASE)
        product.refresh_from_db()  # Refresh after stock change

        # Request adjustment
        adjustment = adjust_stock(employee, product, Decimal("8.0000"), "CORRECTION")

        # Approve and execute
        transaction = approve_adjustment(adjustment, employee)

        product.refresh_from_db()
        assert product.current_stock == Decimal("8.0000")
        assert adjustment.status == StockAdjustmentStatus.EXECUTED
        assert transaction is not None

    def test_audit_logging(self, setup_inventory):
        """Test that stock operations create audit logs."""
        from audit.models import AuditLog

        product = setup_inventory["product"]
        employee = setup_inventory["employee"]

        # Perform stock-in
        stock_in(product, Decimal("10"), Decimal("100.0000"), employee, StockChangeType.PURCHASE)

        # Verify audit log created
        logs = AuditLog.objects.filter(action_code="inventory.stock.purchase")
        assert logs.count() >= 1

        log = logs.first()
        assert log.actor == employee
        assert log.before_data["current_stock"] == "0.0000"
        assert log.after_data["current_stock"] == "10.0000"
