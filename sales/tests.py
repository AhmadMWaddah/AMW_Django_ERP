"""
-- AMW Django ERP - Sales Tests --

Constitution Section 13: Testing & Verification Law
- Every critical business feature requires tests
- Tests should validate business behavior, not only model creation
- Sales-confirmation flows are high-priority test domains

Test Coverage:
- Models: Customer, CustomerCategory, SalesOrder, SalesOrderItem
- Operations: confirm_order, void_order, generate_order_number
- Snapshot Integrity: Price preservation after product price changes
- Atomic Safety: Insufficient stock handling
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from inventory.models import Product
from sales.logic.pricing import calculate_line_total, calculate_order_totals
from sales.models import (
    Customer,
    CustomerCategory,
    OrderStatus,
    PaymentStatus,
    SalesOrder,
    SalesOrderItem,
)
from sales.operations.orders import (
    confirm_order,
    generate_order_number,
    update_payment,
    void_order,
)


@pytest.mark.django_db
class TestCustomerCategoryModel:
    """Test CustomerCategory model functionality."""

    def test_create_category(self):
        """Test basic category creation."""
        category = CustomerCategory.objects.create(
            name="Corporate",
            description="Enterprise customers",
        )

        assert category.name == "Corporate"
        assert category.slug == "corporate"
        assert category.description == "Enterprise customers"
        assert category.parent is None

    def test_category_auto_slug(self):
        """Test automatic slug generation."""
        category = CustomerCategory.objects.create(name="Small Business")
        assert category.slug == "small-business"

    def test_category_hierarchy(self):
        """Test parent-child category relationships."""
        parent = CustomerCategory.objects.create(name="Corporate")
        child = CustomerCategory.objects.create(name="Enterprise", parent=parent)

        assert child.parent == parent
        assert child in parent.children.all()

    def test_category_full_path(self):
        """Test full category path including ancestors."""
        level1 = CustomerCategory.objects.create(name="Level 1")
        level2 = CustomerCategory.objects.create(name="Level 2", parent=level1)
        level3 = CustomerCategory.objects.create(name="Level 3", parent=level2)

        assert level3.get_full_path() == "Level 1 / Level 2 / Level 3"

    def test_category_circular_reference(self):
        """Test prevention of circular references."""
        category = CustomerCategory.objects.create(name="Test")
        category.parent = category

        with pytest.raises(ValidationError):
            category.clean()

    def test_soft_delete(self):
        """Test soft delete functionality."""
        category = CustomerCategory.objects.create(name="To Delete")
        category_id = category.id

        # Soft delete
        category.delete()

        # Should not appear in default queryset
        assert CustomerCategory.objects.filter(id=category_id).count() == 0

        # Should appear in all_with_deleted
        assert CustomerCategory.objects.all_with_deleted().filter(id=category_id).count() == 1

        # Restore
        category.undelete()
        assert CustomerCategory.objects.filter(id=category_id).count() == 1


@pytest.mark.django_db
class TestCustomerModel:
    """Test Customer model functionality."""

    def test_create_customer(self):
        """Test basic customer creation."""
        category = CustomerCategory.objects.create(name="Retail")
        customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            category=category,
        )

        assert customer.name == "John Doe"
        assert customer.email == "john@example.com"
        assert customer.category == category

    def test_customer_without_email(self):
        """Test customer can be created without email."""
        category = CustomerCategory.objects.create(name="Retail")
        customer = Customer.objects.create(
            name="Walk-in Customer",
            category=category,
        )

        assert customer.email == ""
        assert customer.name == "Walk-in Customer"

    def test_customer_name_required(self):
        """Test customer name is required."""
        category = CustomerCategory.objects.create(name="Retail")
        customer = Customer(name="   ", category=category)

        with pytest.raises(ValidationError):
            customer.clean()

    def test_soft_delete(self):
        """Test soft delete functionality."""
        category = CustomerCategory.objects.create(name="Retail")
        customer = Customer.objects.create(name="Test Customer", category=category)
        customer_id = customer.id

        # Soft delete
        customer.delete()

        # Should not appear in default queryset
        assert Customer.objects.filter(id=customer_id).count() == 0

        # Should appear in all_with_deleted
        assert Customer.objects.all_with_deleted().filter(id=customer_id).count() == 1


@pytest.mark.django_db
class TestSalesOrderModel:
    """Test SalesOrder model functionality."""

    @pytest.fixture
    def setup_customer(self):
        """Create test customer."""
        category = CustomerCategory.objects.create(name="Retail")
        return Customer.objects.create(
            name="Test Customer",
            email="test@example.com",
            category=category,
            shipping_address="123 Test St",
        )

    @pytest.fixture
    def setup_employee(self):
        """Create test employee."""
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="sales@amw.io",
            password="test123",
            first_name="Sales",
            last_name="Rep",
        )

    def test_create_draft_order(self, setup_customer, setup_employee):
        """Test creating a draft sales order."""
        order_number = generate_order_number()
        order = SalesOrder.objects.create(
            order_number=order_number,
            customer=setup_customer,
            created_by=setup_employee,
            shipping_address_snapshot=setup_customer.shipping_address,
        )

        assert order.status == OrderStatus.DRAFT
        assert order.payment_status == PaymentStatus.PENDING
        assert order.order_number.startswith("#Eg-")
        assert order.total_amount == Decimal("0.0000")

    def test_order_str_representation(self, setup_customer, setup_employee):
        """Test order string representation."""
        order_number = generate_order_number()
        order = SalesOrder.objects.create(
            order_number=order_number,
            customer=setup_customer,
            created_by=setup_employee,
        )

        assert str(order) == f"{order.order_number} - {setup_customer.name}"

    def test_payment_validation(self, setup_customer, setup_employee):
        """Test payment amount cannot exceed total."""
        order_number = generate_order_number()
        order = SalesOrder.objects.create(
            order_number=order_number,
            customer=setup_customer,
            created_by=setup_employee,
            total_amount=Decimal("100.0000"),
            amount_paid=Decimal("50.0000"),
        )

        order.amount_paid = Decimal("150.0000")
        with pytest.raises(ValidationError):
            order.clean()

    def test_get_amount_due(self, setup_customer, setup_employee):
        """Test amount due calculation."""
        order_number = generate_order_number()
        order = SalesOrder.objects.create(
            order_number=order_number,
            customer=setup_customer,
            created_by=setup_employee,
            total_amount=Decimal("100.0000"),
            amount_paid=Decimal("40.0000"),
        )

        assert order.get_amount_due() == Decimal("60.0000")

    def test_update_payment_status(self, setup_customer, setup_employee):
        """Test payment status auto-update."""
        order_number = generate_order_number()
        order = SalesOrder.objects.create(
            order_number=order_number,
            customer=setup_customer,
            created_by=setup_employee,
            total_amount=Decimal("100.0000"),
            amount_paid=Decimal("0.0000"),
        )

        # Pending
        assert order.payment_status == PaymentStatus.PENDING

        # Partially paid
        order.amount_paid = Decimal("50.0000")
        order.update_payment_status()
        assert order.payment_status == PaymentStatus.PARTIALLY_PAID

        # Fully paid
        order.amount_paid = Decimal("100.0000")
        order.update_payment_status()
        assert order.payment_status == PaymentStatus.PAID


@pytest.mark.django_db
class TestSalesOrderItemModel:
    """Test SalesOrderItem model functionality."""

    @pytest.fixture
    def setup_order(self):
        """Create test order with customer."""
        from accounts.models import Employee

        category = CustomerCategory.objects.create(name="Retail")
        customer = Customer.objects.create(name="Test Customer", category=category)
        employee = Employee.objects.create_user(
            email="sales@amw.io",
            password="test123",
        )

        return SalesOrder.objects.create(
            customer=customer,
            created_by=employee,
        )

    @pytest.fixture
    def setup_product(self):
        """Create test product."""
        from inventory.models import Category

        category = Category.objects.create(name="Test")
        return Product.objects.create(
            sku="TEST-001",
            name="Test Product",
            category=category,
            current_stock=Decimal("100.0000"),
            wac_price=Decimal("50.0000"),
        )

    def test_create_order_item(self, setup_order, setup_product):
        """Test creating order item."""
        item = SalesOrderItem.objects.create(
            order=setup_order,
            product=setup_product,
            quantity=Decimal("2.0000"),
            snapshot_unit_price=Decimal("50.0000"),
        )

        assert item.quantity == Decimal("2.0000")
        assert item.snapshot_unit_price == Decimal("50.0000")
        assert item.total_price == Decimal("100.0000")

    def test_total_price_auto_calculated(self, setup_order, setup_product):
        """Test total_price is auto-calculated on save."""
        item = SalesOrderItem(
            order=setup_order,
            product=setup_product,
            quantity=Decimal("3.0000"),
            snapshot_unit_price=Decimal("25.5000"),
        )
        item.save()

        assert item.total_price == Decimal("76.5000")

    def test_quantity_must_be_positive(self, setup_order, setup_product):
        """Test quantity validation."""
        item = SalesOrderItem(
            order=setup_order,
            product=setup_product,
            quantity=Decimal("-1.0000"),
            snapshot_unit_price=Decimal("50.0000"),
        )

        with pytest.raises(ValidationError):
            item.clean()

    def test_price_cannot_be_negative(self, setup_order, setup_product):
        """Test unit price validation."""
        item = SalesOrderItem(
            order=setup_order,
            product=setup_product,
            quantity=Decimal("1.0000"),
            snapshot_unit_price=Decimal("-10.0000"),
        )

        with pytest.raises(ValidationError):
            item.clean()


@pytest.mark.django_db
class TestOrderOperations:
    """Test sales order operations with inventory integration."""

    @pytest.fixture
    def setup_complete_order(self):
        """Create complete order with items and stock."""
        from accounts.models import Employee
        from inventory.models import Category

        # Create employee
        employee = Employee.objects.create_user(
            email="sales@amw.io",
            password="test123",
        )

        # Create customer
        category = CustomerCategory.objects.create(name="Retail")
        customer = Customer.objects.create(
            name="Test Customer",
            category=category,
            shipping_address="123 Test St",
        )

        # Create product with stock
        product_category = Category.objects.create(name="Test")
        product = Product.objects.create(
            sku="TEST-001",
            name="Test Product",
            category=product_category,
            current_stock=Decimal("50.0000"),
            wac_price=Decimal("100.0000"),
        )

        # Create order
        order_number = generate_order_number()
        order = SalesOrder.objects.create(
            order_number=order_number,
            customer=customer,
            created_by=employee,
            shipping_address_snapshot=customer.shipping_address,
        )

        # Add order item
        SalesOrderItem.objects.create(
            order=order,
            product=product,
            quantity=Decimal("5.0000"),
            snapshot_unit_price=Decimal("100.0000"),
        )

        return {
            "order": order,
            "product": product,
            "employee": employee,
        }

    def test_confirm_order_deducts_stock(self, setup_complete_order):
        """Verify inventory levels drop on order confirmation."""
        order = setup_complete_order["order"]
        product = setup_complete_order["product"]
        employee = setup_complete_order["employee"]

        # Capture initial stock
        initial_stock = product.current_stock

        # Confirm order
        confirm_order(order, employee)

        # Verify stock deducted
        product.refresh_from_db()
        assert product.current_stock == initial_stock - Decimal("5.0000")

    def test_void_order_restores_stock(self, setup_complete_order):
        """Verify inventory levels return on order void."""
        order = setup_complete_order["order"]
        product = setup_complete_order["product"]
        employee = setup_complete_order["employee"]

        # Confirm first
        confirm_order(order, employee)

        # Capture confirmed stock (refresh from DB)
        product.refresh_from_db()
        confirmed_stock = product.current_stock

        # Void order
        void_order(order, employee, reason="Customer cancelled")

        # Verify stock restored
        product.refresh_from_db()
        assert product.current_stock == confirmed_stock + Decimal("5.0000")

    def test_price_snapshot_integrity(self, setup_complete_order):
        """Verify order item price remains unchanged after product price change."""
        order = setup_complete_order["order"]
        product = setup_complete_order["product"]
        employee = setup_complete_order["employee"]

        # Capture original price
        original_price = product.wac_price
        item = order.items.first()

        # Confirm order
        confirm_order(order, employee)

        # Change product price
        product.wac_price = Decimal("999.0000")
        product.save()

        # Verify order item price unchanged
        item.refresh_from_db()
        assert item.snapshot_unit_price == original_price
        assert item.snapshot_unit_price != Decimal("999.0000")

    def test_insufficient_stock_fails(self, setup_complete_order):
        """Verify confirm_order raises error if stock is too low."""
        order = setup_complete_order["order"]
        product = setup_complete_order["product"]
        employee = setup_complete_order["employee"]

        # Reduce stock to insufficient level
        product.current_stock = Decimal("2.0000")
        product.save()

        # Try to confirm (should fail)
        with pytest.raises(ValueError, match="Insufficient stock"):
            confirm_order(order, employee)

        # Verify order status unchanged
        order.refresh_from_db()
        assert order.status == OrderStatus.DRAFT

    def test_cannot_confirm_non_draft_order(self, setup_complete_order):
        """Test only draft orders can be confirmed."""
        order = setup_complete_order["order"]
        employee = setup_complete_order["employee"]

        # Confirm first
        confirm_order(order, employee)

        # Try to confirm again
        with pytest.raises(ValueError, match="Only DRAFT orders can be confirmed"):
            confirm_order(order, employee)

    def test_cannot_void_shipped_order(self, setup_complete_order):
        """Test shipped orders cannot be voided."""
        order = setup_complete_order["order"]
        employee = setup_complete_order["employee"]

        # Manually set to shipped
        order.status = OrderStatus.SHIPPED
        order.save()

        # Try to void
        with pytest.raises(ValueError, match="Cannot void order with status SHIPPED"):
            void_order(order, employee)


@pytest.mark.django_db
class TestOrderNumbering:
    """Test atomic order numbering system."""

    @pytest.fixture
    def setup_employee_and_customer(self):
        """Create employee and customer."""
        from accounts.models import Employee

        category = CustomerCategory.objects.create(name="Retail")
        customer = Customer.objects.create(name="Test Customer", category=category)
        employee = Employee.objects.create_user(
            email="sales@amw.io",
            password="test123",
        )

        return {"customer": customer, "employee": employee}

    def test_generate_order_number_format(self, setup_employee_and_customer):
        """Test order number format is #Eg-00001."""
        customer = setup_employee_and_customer["customer"]
        employee = setup_employee_and_customer["employee"]

        order_number = generate_order_number()
        order = SalesOrder.objects.create(
            order_number=order_number,
            customer=customer,
            created_by=employee,
        )

        assert order.order_number.startswith("#Eg-")
        assert len(order.order_number) == 9  # #Eg-00001

    def test_generate_order_number_sequential(self, setup_employee_and_customer):
        """Test order numbers are sequential."""
        customer = setup_employee_and_customer["customer"]
        employee = setup_employee_and_customer["employee"]

        order_number1 = generate_order_number()
        order1 = SalesOrder.objects.create(
            order_number=order_number1,
            customer=customer,
            created_by=employee,
        )
        order_number2 = generate_order_number()
        order2 = SalesOrder.objects.create(
            order_number=order_number2,
            customer=customer,
            created_by=employee,
        )

        # Extract numbers
        num1 = int(order1.order_number.split("-")[1])
        num2 = int(order2.order_number.split("-")[1])

        assert num2 == num1 + 1


@pytest.mark.django_db
class TestPaymentOperations:
    """Test payment tracking operations."""

    @pytest.fixture
    def setup_order_with_totals(self):
        """Create order with totals."""
        from accounts.models import Employee

        category = CustomerCategory.objects.create(name="Retail")
        customer = Customer.objects.create(name="Test Customer", category=category)
        employee = Employee.objects.create_user(
            email="sales@amw.io",
            password="test123",
        )

        order_number = generate_order_number()
        return SalesOrder.objects.create(
            order_number=order_number,
            customer=customer,
            created_by=employee,
            total_amount=Decimal("100.0000"),
        )

    def test_update_payment_partial(self, setup_order_with_totals):
        """Test partial payment updates status correctly."""
        order = setup_order_with_totals
        employee = order.created_by

        # Make partial payment
        update_payment(order, Decimal("40.0000"), employee)

        order.refresh_from_db()
        assert order.amount_paid == Decimal("40.0000")
        assert order.payment_status == PaymentStatus.PARTIALLY_PAID

    def test_update_payment_full(self, setup_order_with_totals):
        """Test full payment updates status to PAID."""
        order = setup_order_with_totals
        employee = order.created_by

        # Make full payment
        update_payment(order, Decimal("100.0000"), employee)

        order.refresh_from_db()
        assert order.amount_paid == Decimal("100.0000")
        assert order.payment_status == PaymentStatus.PAID

    def test_update_payment_exceeds_total(self, setup_order_with_totals):
        """Test payment cannot exceed total."""
        order = setup_order_with_totals
        employee = order.created_by

        with pytest.raises(ValueError, match="Payment would exceed total"):
            update_payment(order, Decimal("150.0000"), employee)

    def test_update_payment_negative(self, setup_order_with_totals):
        """Test payment must be positive."""
        order = setup_order_with_totals
        employee = order.created_by

        with pytest.raises(ValueError, match="Payment amount must be positive"):
            update_payment(order, Decimal("-10.0000"), employee)


@pytest.mark.django_db
class TestPricingLogic:
    """Test pricing calculation logic."""

    def test_calculate_line_total(self):
        """Test line total calculation."""
        total = calculate_line_total(Decimal("3.0000"), Decimal("25.5000"))
        assert total == Decimal("76.5000")

    def test_calculate_line_total_rounding(self):
        """Test line total uses ROUND_HALF_UP."""
        # 3.333 * 3.333 = 11.108889 -> should round to 11.1089
        total = calculate_line_total(Decimal("3.3333"), Decimal("3.3333"))
        assert total == Decimal("11.1109")

    def test_calculate_order_totals(self):
        """Test order totals calculation."""
        from inventory.models import Category

        # Create order
        category = CustomerCategory.objects.create(name="Retail")
        customer = Customer.objects.create(name="Test", category=category)
        from accounts.models import Employee

        employee = Employee.objects.create_user(email="test@amw.io", password="test")
        order_number = generate_order_number()
        order = SalesOrder.objects.create(
            order_number=order_number,
            customer=customer,
            created_by=employee,
        )

        # Add items
        product_category = Category.objects.create(name="Test")
        product = Product.objects.create(
            sku="TEST-001",
            name="Test",
            category=product_category,
        )

        SalesOrderItem.objects.create(
            order=order,
            product=product,
            quantity=Decimal("2.0000"),
            snapshot_unit_price=Decimal("50.0000"),
        )

        # Calculate totals
        subtotal, tax, total = calculate_order_totals(order)

        assert subtotal == Decimal("100.0000")
        assert tax == Decimal("14.0000")  # 14% tax
        assert total == Decimal("114.0000")
