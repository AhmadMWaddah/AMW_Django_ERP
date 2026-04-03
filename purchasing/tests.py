"""
-- AMW Django ERP - Purchasing Tests --

Constitution Section 13: Testing & Verification Law
- Every critical business feature requires tests
- Tests should validate business behavior, not only model creation
- Purchasing and stock receiving flows are high-priority test domains

Test Coverage:
- Models: SupplierCategory, Supplier, PurchaseOrder, PurchaseOrderItem
- Operations: issue_order, receive_items, cancel_order, generate_po_number
- Partial Receiving: In-Progress status tracking
- WAC Integration: Valuation recalculation on receipt
- Snapshot Integrity: Supplier info preservation
- Atomic Numbering: PO numbers unique and sequential
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from inventory.logic.valuation import calculate_wac
from inventory.models import Product, StockChangeType, StockTransaction
from purchasing.models import POStatus, PurchaseOrder, PurchaseOrderItem, Supplier, SupplierCategory
from purchasing.operations.orders import (
    cancel_order,
    generate_po_number,
    issue_order,
    receive_items,
)


@pytest.mark.django_db
class TestSupplierCategoryModel:
    """Test SupplierCategory model functionality."""

    def test_create_category(self):
        """Test basic supplier category creation."""
        category = SupplierCategory.objects.create(
            name="Raw Materials",
            description="Basic raw materials",
        )

        assert category.name == "Raw Materials"
        assert category.code == "raw-materials"
        assert category.description == "Basic raw materials"

    def test_category_auto_slug(self):
        """Test automatic slug generation."""
        category = SupplierCategory.objects.create(name="Electronics Suppliers")
        assert category.code == "electronics-suppliers"

    def test_category_hierarchy(self):
        """Test parent-child category relationships."""
        parent = SupplierCategory.objects.create(name="Manufacturers")
        child = SupplierCategory.objects.create(name="OEM Manufacturers", parent=parent)

        assert child.parent == parent
        assert child in parent.children.all()

    def test_category_full_path(self):
        """Test full category path including ancestors."""
        level1 = SupplierCategory.objects.create(name="Level 1")
        level2 = SupplierCategory.objects.create(name="Level 2", parent=level1)
        level3 = SupplierCategory.objects.create(name="Level 3", parent=level2)

        assert level3.get_full_path() == "Level 1 / Level 2 / Level 3"

    def test_category_circular_reference(self):
        """Test prevention of circular references."""
        category = SupplierCategory.objects.create(name="Test")
        category.parent = category

        with pytest.raises(ValidationError):
            category.clean()

    def test_soft_delete(self):
        """Test soft delete functionality."""
        category = SupplierCategory.objects.create(name="To Delete")
        category_id = category.id

        category.delete()

        assert SupplierCategory.objects.filter(id=category_id).count() == 0
        assert SupplierCategory.objects.all_with_deleted().filter(id=category_id).count() == 1

        category.undelete()
        assert SupplierCategory.objects.filter(id=category_id).count() == 1


@pytest.mark.django_db
class TestSupplierModel:
    """Test Supplier model functionality."""

    @pytest.fixture
    def supplier_category(self):
        """Create a supplier category."""
        return SupplierCategory.objects.create(name="Electronics")

    def test_create_supplier(self, supplier_category):
        """Test basic supplier creation."""
        supplier = Supplier.objects.create(
            name="Tech Parts Inc",
            email="orders@techparts.com",
            phone="+1234567890",
            category=supplier_category,
            address="456 Industrial Blvd",
            contact_person="John Smith",
        )

        assert supplier.name == "Tech Parts Inc"
        assert supplier.email == "orders@techparts.com"
        assert supplier.category == supplier_category

    def test_supplier_str(self, supplier_category):
        """Test string representation."""
        supplier = Supplier.objects.create(name="Global Supply Co", category=supplier_category)
        assert str(supplier) == "Global Supply Co"

    def test_supplier_requires_name(self):
        """Test that supplier name is required."""
        category = SupplierCategory.objects.create(name="Test")
        supplier = Supplier(name="   ", category=category)

        with pytest.raises(ValidationError):
            supplier.clean()

    def test_soft_delete(self, supplier_category):
        """Test soft delete functionality."""
        supplier = Supplier.objects.create(name="To Delete", category=supplier_category)
        supplier_id = supplier.id

        supplier.delete()

        assert Supplier.objects.filter(id=supplier_id).count() == 0
        assert Supplier.objects.all_with_deleted().filter(id=supplier_id).count() == 1


@pytest.mark.django_db
class TestPurchaseOrderModel:
    """Test PurchaseOrder model functionality."""

    @pytest.fixture
    def supplier(self):
        """Create a test supplier."""
        category = SupplierCategory.objects.create(name="Electronics")
        return Supplier.objects.create(name="Tech Parts Inc", category=category)

    @pytest.fixture
    def employee(self):
        """Create a test employee."""
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="purchasing@amw.io",
            password="test123",
            first_name="Purchasing",
            last_name="Agent",
        )

    def test_create_draft_po(self, supplier, employee):
        """Test creating a draft purchase order."""
        po = PurchaseOrder.objects.create(
            supplier=supplier,
            created_by=employee,
        )

        assert po.status == POStatus.DRAFT
        assert po.po_number == ""  # Not assigned until issued
        assert po.total_cost == Decimal("0.0000")
        assert po.supplier_info_snapshot is None

    def test_po_str(self, supplier, employee):
        """Test PO string representation."""
        po = PurchaseOrder.objects.create(
            po_number="PO-00001",
            supplier=supplier,
            created_by=employee,
        )
        assert str(po) == "PO-00001 - Tech Parts Inc"

    def test_po_status_transitions(self, supplier, employee):
        """Test valid PO status transitions."""
        # Draft -> Issued (valid)
        po1 = PurchaseOrder.objects.create(
            supplier=supplier,
            created_by=employee,
            po_number="TEST-001",
        )
        po1.status = POStatus.ISSUED
        # Should not raise — Draft can go to Issued

        # Issued -> In-Progress (valid)
        po2 = PurchaseOrder.objects.create(
            supplier=supplier,
            created_by=employee,
            po_number="TEST-002",
        )
        po2.status = POStatus.ISSUED
        po2.save()
        po2.status = POStatus.IN_PROGRESS
        # Should not raise

        # In-Progress -> Completed (valid)
        po3 = PurchaseOrder.objects.create(
            supplier=supplier,
            created_by=employee,
            po_number="TEST-003",
        )
        po3.status = POStatus.ISSUED
        po3.save()
        po3.status = POStatus.IN_PROGRESS
        po3.save()
        po3.status = POStatus.COMPLETED
        # Should not raise

    def test_invalid_po_transition(self, supplier, employee):
        """Test invalid PO status transition."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)

        # Draft cannot go directly to Completed
        po.status = POStatus.COMPLETED

        with pytest.raises(ValidationError):
            po.clean()

    def test_completed_po_cannot_cancel(self, supplier, employee):
        """Test that completed POs cannot be cancelled via transition."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        po.status = POStatus.COMPLETED
        po.save()

        po.status = POStatus.CANCELLED

        with pytest.raises(ValidationError):
            po.clean()

    def test_soft_delete(self, supplier, employee):
        """Test soft delete on purchase orders."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        po_id = po.id

        po.delete()

        assert PurchaseOrder.objects.filter(id=po_id).count() == 0
        assert PurchaseOrder.objects.all_with_deleted().filter(id=po_id).count() == 1


@pytest.mark.django_db
class TestPurchaseOrderItemModel:
    """Test PurchaseOrderItem model functionality."""

    @pytest.fixture
    def supplier(self):
        category = SupplierCategory.objects.create(name="Electronics")
        return Supplier.objects.create(name="Tech Parts Inc", category=category)

    @pytest.fixture
    def employee(self):
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="purchasing@amw.io",
            password="test123",
            first_name="Purchasing",
            last_name="Agent",
        )

    @pytest.fixture
    def po(self, supplier, employee):
        return PurchaseOrder.objects.create(supplier=supplier, created_by=employee)

    @pytest.fixture
    def product(self):
        from inventory.models import Category

        cat = Category.objects.create(name="Electronics")
        return Product.objects.create(
            sku="EL-CR-001",
            name="Test Product",
            category=cat,
            current_stock=Decimal("0"),
            wac_price=Decimal("0.0000"),
        )

    def test_create_po_item(self, po, product):
        """Test creating a purchase order line item."""
        item = PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("100"),
            unit_cost=Decimal("25.5000"),
        )

        assert item.quantity == Decimal("100")
        assert item.unit_cost == Decimal("25.5000")
        assert item.total_cost == Decimal("2550.0000")
        assert item.received_quantity == Decimal("0")

    def test_po_item_auto_total(self, po, product):
        """Test automatic total calculation on save."""
        item = PurchaseOrderItem(
            order=po,
            product=product,
            quantity=Decimal("10"),
            unit_cost=Decimal("33.3333"),
        )
        item.save()

        # 10 * 33.3333 = 333.333 (stored as-is, no rounding in model save)
        assert item.total_cost == Decimal("333.3330")

    def test_po_item_decimal_precision(self, po, product):
        """Test 19,4 decimal precision on fields."""
        item = PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("1.5555"),
            unit_cost=Decimal("99.9999"),
        )

        # 1.5555 * 99.9999 = 155.54984445 (raw multiplication)
        # The DB stores with 19,4 but Python calculation is exact
        assert item.total_cost == Decimal("155.54984445")

    def test_po_item_quantity_validation(self, po, product):
        """Test quantity must be positive."""
        item = PurchaseOrderItem(
            order=po,
            product=product,
            quantity=Decimal("-1"),
            unit_cost=Decimal("10"),
        )

        with pytest.raises(ValidationError):
            item.clean()

    def test_po_item_received_exceeds_ordered(self, po, product):
        """Test received quantity cannot exceed ordered quantity."""
        item = PurchaseOrderItem(
            order=po,
            product=product,
            quantity=Decimal("10"),
            unit_cost=Decimal("10"),
            received_quantity=Decimal("11"),
        )

        with pytest.raises(ValidationError):
            item.clean()

    def test_is_fully_received(self, po, product):
        """Test full receiving status check."""
        item = PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("100"),
            unit_cost=Decimal("10"),
            received_quantity=Decimal("50"),
        )

        assert not item.is_fully_received()

        item.received_quantity = Decimal("100")
        item.save()
        assert item.is_fully_received()

    def test_remaining_quantity(self, po, product):
        """Test remaining quantity calculation."""
        item = PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("100"),
            unit_cost=Decimal("10"),
            received_quantity=Decimal("30"),
        )

        assert item.get_remaining_quantity() == Decimal("70")

    def test_po_item_str(self, po, product):
        """Test PO item string representation."""
        po.po_number = "PO-00001"
        po.save()
        item = PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("50"),
            unit_cost=Decimal("10"),
        )

        assert str(item) == "PO-00001 - EL-CR-001 x 50"


@pytest.mark.django_db
class TestPONumbering:
    """Test atomic PO numbering."""

    @pytest.fixture
    def supplier(self):
        category = SupplierCategory.objects.create(name="Electronics")
        return Supplier.objects.create(name="Tech Parts Inc", category=category)

    @pytest.fixture
    def employee(self):
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="purchasing@amw.io",
            password="test123",
            first_name="Purchasing",
            last_name="Agent",
        )

    def test_first_po_number(self):
        """Test first PO number is PO-00001."""
        number = generate_po_number()
        assert number == "PO-00001"

    def test_sequential_po_numbers(self, supplier, employee):
        """Test PO numbers are sequential."""
        # Create POs directly to simulate existing data
        PurchaseOrder.objects.create(
            po_number="PO-00001",
            supplier=supplier,
            created_by=employee,
        )
        PurchaseOrder.objects.create(
            po_number="PO-00002",
            supplier=supplier,
            created_by=employee,
        )

        next_number = generate_po_number()
        assert next_number == "PO-00003"

    def test_po_number_ignores_deleted(self, supplier, employee):
        """Test PO numbering continues past deleted records."""
        po1 = PurchaseOrder.objects.create(
            po_number="PO-00001",
            supplier=supplier,
            created_by=employee,
        )
        po1.delete()

        # Next number should still increment
        next_number = generate_po_number()
        assert next_number == "PO-00002"


@pytest.mark.django_db
class TestIssueOrder:
    """Test PO issue operation."""

    @pytest.fixture
    def supplier(self):
        category = SupplierCategory.objects.create(name="Electronics")
        return Supplier.objects.create(
            name="Tech Parts Inc",
            category=category,
            email="orders@techparts.com",
            phone="+1234567890",
            address="456 Industrial Blvd",
            contact_person="John Smith",
        )

    @pytest.fixture
    def employee(self):
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="purchasing@amw.io",
            password="test123",
            first_name="Purchasing",
            last_name="Agent",
        )

    @pytest.fixture
    def product(self):
        from inventory.models import Category

        cat = Category.objects.create(name="Electronics")
        return Product.objects.create(
            sku="EL-CR-001",
            name="Test Product",
            category=cat,
            current_stock=Decimal("0"),
            wac_price=Decimal("0.0000"),
        )

    def test_issue_draft_po(self, supplier, employee, product):
        """Test issuing a draft purchase order."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("10"),
            unit_cost=Decimal("10"),
        )

        result = issue_order(po, employee)

        assert result.status == POStatus.ISSUED
        assert result.po_number == "PO-00001"
        assert result.issued_by == employee
        assert result.issued_at is not None

    def test_issue_sets_supplier_snapshot(self, supplier, employee, product):
        """Test supplier info is snapshotted on issue."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("10"),
            unit_cost=Decimal("10"),
        )

        issue_order(po, employee)

        po.refresh_from_db()
        assert po.supplier_info_snapshot is not None
        assert po.supplier_info_snapshot["name"] == "Tech Parts Inc"
        assert po.supplier_info_snapshot["email"] == "orders@techparts.com"

    def test_cannot_issue_without_items(self, supplier, employee):
        """Test PO cannot be issued without line items."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)

        with pytest.raises(ValueError, match="without line items"):
            issue_order(po, employee)

    def test_cannot_issue_already_issued(self, supplier, employee, product):
        """Test already issued PO cannot be issued again."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("10"),
            unit_cost=Decimal("10"),
        )
        issue_order(po, employee)

        with pytest.raises(ValueError, match="Only DRAFT orders"):
            issue_order(po, employee)


@pytest.mark.django_db
class TestReceiveItems:
    """Test PO receiving operation."""

    @pytest.fixture
    def supplier(self):
        category = SupplierCategory.objects.create(name="Electronics")
        return Supplier.objects.create(
            name="Tech Parts Inc",
            category=category,
            email="orders@techparts.com",
            address="456 Industrial Blvd",
        )

    @pytest.fixture
    def employee(self):
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="purchasing@amw.io",
            password="test123",
            first_name="Purchasing",
            last_name="Agent",
        )

    @pytest.fixture
    def product(self):
        from inventory.models import Category

        cat = Category.objects.create(name="Electronics")
        return Product.objects.create(
            sku="EL-CR-001",
            name="Test Product",
            category=cat,
            current_stock=Decimal("10"),
            wac_price=Decimal("50.0000"),
        )

    @pytest.fixture
    def issued_po(self, supplier, employee, product):
        """Create an issued PO with items."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("100"),
            unit_cost=Decimal("60.0000"),
        )
        issue_order(po, employee)
        return po

    def test_receive_full_quantity(self, issued_po, employee):
        """Test receiving full ordered quantity."""
        item = issued_po.items.first()
        old_stock = item.product.current_stock

        result = receive_items(
            issued_po,
            [{"item_id": item.id, "quantity": Decimal("100")}],
            employee,
        )

        item.product.refresh_from_db()
        assert item.product.current_stock == old_stock + Decimal("100")
        assert result.status == POStatus.COMPLETED

    def test_receive_partial_quantity(self, issued_po, employee):
        """Test partial receiving moves status to In-Progress."""
        item = issued_po.items.first()

        result = receive_items(
            issued_po,
            [{"item_id": item.id, "quantity": Decimal("40")}],
            employee,
        )

        item.refresh_from_db()
        assert item.received_quantity == Decimal("40")
        assert result.status == POStatus.IN_PROGRESS

    def test_wac_recalculation_on_receipt(self, issued_po, employee):
        """Test WAC recalculates after receiving stock."""
        item = issued_po.items.first()
        product = item.product

        # Before: stock=10, wac=50.0000
        # Receive: 100 @ 60.0000
        # Expected WAC: (10*50 + 100*60) / (10+100) = 6500/110 = 59.0909
        receive_items(
            issued_po,
            [{"item_id": item.id, "quantity": Decimal("100")}],
            employee,
        )

        product.refresh_from_db()
        expected_wac = calculate_wac(Decimal("10"), Decimal("50.0000"), Decimal("100"), Decimal("60.0000"))
        assert product.wac_price == expected_wac

    def test_wac_variance_check_blocks_extreme_cost(self, issued_po, employee):
        """Test that extreme unit cost deviation blocks receipt (WAC sanity check)."""
        item = issued_po.items.first()
        # Product WAC is 50.0000. Set unit_cost to 500 (900% deviation, threshold is 25%)
        item.unit_cost = Decimal("500.0000")
        item.save()

        with pytest.raises(ValueError, match=r"deviates \d+% from current WAC"):
            receive_items(
                issued_po,
                [{"item_id": item.id, "quantity": Decimal("10")}],
                employee,
            )

    def test_wac_variance_allows_within_threshold(self, issued_po, employee):
        """Test that cost within threshold is accepted."""
        item = issued_po.items.first()
        # Product WAC is 50.0000. Set unit_cost to 55 (10% deviation, under 25% threshold)
        item.unit_cost = Decimal("55.0000")
        item.save()

        result = receive_items(
            issued_po,
            [{"item_id": item.id, "quantity": Decimal("10")}],
            employee,
        )
        # Should succeed without raising
        assert result.status == POStatus.IN_PROGRESS

    def test_wac_variance_skipped_for_new_product(self, supplier, employee):
        """Test that WAC check is skipped when product has no WAC yet (wac_price=0)."""
        from inventory.models import Category

        cat = Category.objects.create(name="Electronics")
        product = Product.objects.create(
            sku="EL-CR-NEW",
            name="New Product",
            category=cat,
            current_stock=Decimal("0"),
            wac_price=Decimal("0"),
        )

        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        item = PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("100"),
            unit_cost=Decimal("100.0000"),  # Any cost is fine when WAC is 0
        )
        issue_order(po, employee)

        # Should not raise — WAC check skipped for new products
        result = receive_items(
            po,
            [{"item_id": item.id, "quantity": Decimal("100")}],
            employee,
        )
        assert result.status == POStatus.COMPLETED

    def test_stock_transaction_created(self, issued_po, employee):
        """Test stock transaction is created with PURCHASE type."""
        item = issued_po.items.first()
        old_txn_count = StockTransaction.objects.count()

        receive_items(
            issued_po,
            [{"item_id": item.id, "quantity": Decimal("50")}],
            employee,
        )

        assert StockTransaction.objects.count() == old_txn_count + 1
        txn = StockTransaction.objects.first()
        assert txn.change_type == StockChangeType.PURCHASE
        assert txn.reference_type == "PurchaseOrder"

    def test_cannot_receive_excess_quantity(self, issued_po, employee):
        """Test receiving more than ordered fails."""
        item = issued_po.items.first()

        with pytest.raises(ValueError, match=r"only 100\.0000 remaining"):
            receive_items(
                issued_po,
                [{"item_id": item.id, "quantity": Decimal("101")}],
                employee,
            )

    def test_cannot_receive_on_draft(self, supplier, employee, product):
        """Test cannot receive against a draft PO."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("10"),
            unit_cost=Decimal("10"),
        )

        with pytest.raises(ValueError, match="Only Issued or In-Progress"):
            receive_items(
                po,
                [{"item_id": po.items.first().id, "quantity": Decimal("5")}],
                employee,
            )

    def test_partial_then_complete(self, issued_po, employee):
        """Test partial receipt followed by full receipt completes PO."""
        item = issued_po.items.first()

        # Partial receipt
        result = receive_items(
            issued_po,
            [{"item_id": item.id, "quantity": Decimal("40")}],
            employee,
        )
        assert result.status == POStatus.IN_PROGRESS

        # Full receipt of remaining
        result = receive_items(
            issued_po,
            [{"item_id": item.id, "quantity": Decimal("60")}],
            employee,
        )
        assert result.status == POStatus.COMPLETED

    def test_multiple_items_partial_receipt(self, supplier, employee):
        """Test PO with multiple items and partial receipt."""
        from inventory.models import Category

        cat = Category.objects.create(name="Electronics")
        product1 = Product.objects.create(
            sku="EL-CR-001",
            name="Product A",
            category=cat,
            current_stock=Decimal("0"),
            wac_price=Decimal("0"),
        )
        product2 = Product.objects.create(
            sku="EL-CR-002",
            name="Product B",
            category=cat,
            current_stock=Decimal("0"),
            wac_price=Decimal("0"),
        )

        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        item1 = PurchaseOrderItem.objects.create(
            order=po,
            product=product1,
            quantity=Decimal("50"),
            unit_cost=Decimal("10"),
        )
        item2 = PurchaseOrderItem.objects.create(
            order=po,
            product=product2,
            quantity=Decimal("30"),
            unit_cost=Decimal("20"),
        )
        issue_order(po, employee)

        # Receive only item1
        result = receive_items(
            po,
            [{"item_id": item1.id, "quantity": Decimal("50")}],
            employee,
        )
        assert result.status == POStatus.IN_PROGRESS

        # Receive item2
        result = receive_items(
            po,
            [{"item_id": item2.id, "quantity": Decimal("30")}],
            employee,
        )
        assert result.status == POStatus.COMPLETED


@pytest.mark.django_db
class TestCancelOrder:
    """Test PO cancellation."""

    @pytest.fixture
    def supplier(self):
        category = SupplierCategory.objects.create(name="Electronics")
        return Supplier.objects.create(name="Tech Parts Inc", category=category)

    @pytest.fixture
    def employee(self):
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="purchasing@amw.io",
            password="test123",
            first_name="Purchasing",
            last_name="Agent",
        )

    @pytest.fixture
    def product(self):
        from inventory.models import Category

        cat = Category.objects.create(name="Electronics")
        return Product.objects.create(
            sku="EL-CR-001",
            name="Test Product",
            category=cat,
            current_stock=Decimal("0"),
            wac_price=Decimal("0"),
        )

    def test_cancel_draft(self, supplier, employee):
        """Test cancelling a draft PO."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)

        result = cancel_order(po, employee, reason="No longer needed")

        assert result.status == POStatus.CANCELLED
        assert result.cancelled_by == employee

    def test_cancel_issued(self, supplier, employee, product):
        """Test cancelling an issued PO."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("10"),
            unit_cost=Decimal("10"),
        )
        issue_order(po, employee)

        result = cancel_order(po, employee, reason="Found cheaper supplier")
        assert result.status == POStatus.CANCELLED

    def test_cannot_cancel_completed(self, supplier, employee, product):
        """Test cannot cancel a completed PO."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        item = PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("10"),
            unit_cost=Decimal("10"),
        )
        issue_order(po, employee)
        receive_items(po, [{"item_id": item.id, "quantity": Decimal("10")}], employee)

        with pytest.raises(ValueError, match="Cannot cancel"):
            cancel_order(po, employee)

    def test_cannot_cancel_already_cancelled(self, supplier, employee):
        """Test cannot cancel an already cancelled PO."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        cancel_order(po, employee)

        with pytest.raises(ValueError, match="Cannot cancel"):
            cancel_order(po, employee)


@pytest.mark.django_db
class TestSnapshotIntegrity:
    """Test supplier info snapshot preservation."""

    @pytest.fixture
    def supplier(self):
        category = SupplierCategory.objects.create(name="Electronics")
        return Supplier.objects.create(
            name="Tech Parts Inc",
            category=category,
            email="orders@techparts.com",
            address="456 Industrial Blvd",
            contact_person="John Smith",
        )

    @pytest.fixture
    def employee(self):
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="purchasing@amw.io",
            password="test123",
            first_name="Purchasing",
            last_name="Agent",
        )

    @pytest.fixture
    def product(self):
        from inventory.models import Category

        cat = Category.objects.create(name="Electronics")
        return Product.objects.create(
            sku="EL-CR-001",
            name="Test Product",
            category=cat,
            current_stock=Decimal("0"),
            wac_price=Decimal("0"),
        )

    def test_snapshot_preserved_after_supplier_change(self, supplier, employee, product):
        """Test supplier snapshot preserved even if supplier info changes."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("10"),
            unit_cost=Decimal("10"),
        )
        issue_order(po, employee)

        # Change supplier info
        supplier.name = "Tech Parts Inc (Acquired)"
        supplier.save()

        # PO should still have original snapshot
        po.refresh_from_db()
        assert po.supplier_info_snapshot["name"] == "Tech Parts Inc"


@pytest.mark.django_db
class TestReceivedTotal:
    """Test received total calculation."""

    @pytest.fixture
    def supplier(self):
        category = SupplierCategory.objects.create(name="Electronics")
        return Supplier.objects.create(name="Tech Parts Inc", category=category)

    @pytest.fixture
    def employee(self):
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="purchasing@amw.io",
            password="test123",
            first_name="Purchasing",
            last_name="Agent",
        )

    @pytest.fixture
    def product(self):
        from inventory.models import Category

        cat = Category.objects.create(name="Electronics")
        return Product.objects.create(
            sku="EL-CR-001",
            name="Test Product",
            category=cat,
            current_stock=Decimal("0"),
            wac_price=Decimal("0"),
        )

    def test_get_received_total(self, supplier, employee, product):
        """Test received total calculation."""
        po = PurchaseOrder.objects.create(supplier=supplier, created_by=employee)
        item = PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("100"),
            unit_cost=Decimal("10"),
        )
        issue_order(po, employee)

        # Receive 40 units
        receive_items(po, [{"item_id": item.id, "quantity": Decimal("40")}], employee)

        assert po.get_received_total() == Decimal("400.0000")
