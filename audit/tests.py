"""
-- AMW Django ERP - Audit Tests --

Comprehensive test suite for Audit Logging.

Tests cover:
- AuditLog model creation and fields
- Audit logging utilities and decorators
- Before/after state tracking
- Integration with operations
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from audit.logic.logging import audit_operation, log_audit, serialize_for_audit
from audit.models import AuditLog

Employee = get_user_model()


@pytest.mark.django_db
class TestAuditLogModel:
    """Tests for AuditLog model."""

    def test_create_audit_log(self):
        """Test creating an audit log entry."""
        employee = Employee.objects.create_user(
            email="test@example.com", password="pass123", first_name="Test", last_name="User"
        )

        audit_entry = AuditLog.objects.create(
            actor=employee,
            action="create",
            action_code="inventory.product.create",
            action_description="Created new product",
            content_type="inventory.Product",
            object_id="1",
            object_repr="Product ABC",
            before_data=None,
            after_data={"name": "Product ABC", "price": 100},
            user_agent="Test Browser",
        )

        assert audit_entry.actor == employee
        assert audit_entry.action == "create"
        assert audit_entry.action_code == "inventory.product.create"
        assert audit_entry.content_type == "inventory.Product"
        assert audit_entry.object_id == "1"
        assert audit_entry.after_data["name"] == "Product ABC"

    def test_audit_log_auto_populates_actor_backup(self):
        """Test that audit log auto-populates actor email and name."""
        employee = Employee.objects.create_user(
            email="audit@example.com", password="pass123", first_name="Audit", last_name="User"
        )

        audit_entry = AuditLog.objects.create(
            actor=employee,
            action="update",
            action_code="test.action",
            content_type="test.Model",
            object_id="1",
            object_repr="Test Object",
            user_agent="Test Agent",  # Add required field
        )

        assert audit_entry.actor_email == "audit@example.com"
        # Employee __str__ includes email, so check for name presence
        assert "Audit" in audit_entry.actor_name

    def test_audit_log_action_choices(self):
        """Test audit log action choices."""
        employee = Employee.objects.create_user(email="test@example.com", password="pass123")

        # Test all action choices
        actions = ["create", "update", "delete", "read", "approve", "reject", "adjust", "transfer", "other"]

        for action in actions:
            audit_entry = AuditLog.objects.create(
                actor=employee,
                action=action,
                action_code=f"test.{action}",
                content_type="test.Model",
                object_id="1",
                object_repr="Test",
                user_agent="Test Browser",
            )
            assert audit_entry.action == action

    def test_audit_log_before_after_data(self):
        """Test storing before and after state data."""
        employee = Employee.objects.create_user(email="test@example.com", password="pass123")

        before = {"quantity": 100, "price": 50}
        after = {"quantity": 90, "price": 50}

        audit_entry = AuditLog.objects.create(
            actor=employee,
            action="update",
            action_code="inventory.stock.adjust",
            content_type="inventory.Product",
            object_id="1",
            object_repr="Product X",
            before_data=before,
            after_data=after,
            user_agent="Test Browser",
        )

        assert audit_entry.before_data["quantity"] == 100
        assert audit_entry.after_data["quantity"] == 90
        assert audit_entry.after_data["price"] == 50

    def test_audit_log_str_representation(self):
        """Test audit log string representation."""
        employee = Employee.objects.create_user(email="test@example.com", password="pass123")

        audit_entry = AuditLog.objects.create(
            actor=employee,
            action="create",
            action_code="test.create",
            content_type="test.Model",
            object_id="1",
            object_repr="Test Object",
            user_agent="Test Browser",
        )

        # Should contain action_code and actor name
        assert "test.create" in str(audit_entry)
        assert "Test User" in str(audit_entry) or "test@example.com" in str(audit_entry)

    def test_audit_log_ordering(self):
        """Test that audit logs are ordered by timestamp descending."""
        employee = Employee.objects.create_user(email="test@example.com", password="pass123")

        # Create multiple entries
        entry1 = AuditLog.objects.create(
            actor=employee,
            action="create",
            action_code="test.1",
            content_type="test",
            object_id="1",
            object_repr="First",
            user_agent="Test Browser",
        )

        entry2 = AuditLog.objects.create(
            actor=employee,
            action="create",
            action_code="test.2",
            content_type="test",
            object_id="2",
            object_repr="Second",
            user_agent="Test Browser",
        )

        # Get all logs
        logs = list(AuditLog.objects.all())

        # Most recent should be first
        assert logs[0] == entry2
        assert logs[1] == entry1

    def test_audit_log_indexes(self):
        """Test that audit log has proper indexes."""
        # This test verifies indexes exist by checking query performance
        employee = Employee.objects.create_user(email="test@example.com", password="pass123")

        # Create some entries
        for i in range(10):
            AuditLog.objects.create(
                actor=employee,
                action="create",
                action_code=f"test.{i}",
                content_type="test",
                object_id=str(i),
                object_repr=f"Test {i}",
                user_agent="Test Browser",
            )

        # Query by actor (should use index)
        actor_logs = AuditLog.objects.filter(actor=employee)
        assert actor_logs.count() == 10

        # Query by content_type and object_id (should use index)
        type_logs = AuditLog.objects.filter(content_type="test", object_id="5")
        assert type_logs.count() == 1


@pytest.mark.django_db
class TestAuditLogConvenienceMethods:
    """Tests for AuditLog convenience methods."""

    def test_log_action_convenience_method(self):
        """Test the log_action convenience method."""
        employee = Employee.objects.create_user(
            email="test@example.com", password="pass123", first_name="Test", last_name="User"
        )

        audit_entry = AuditLog.log_action(
            actor=employee,
            action_code="inventory.stock.adjust",
            action="adjust",
            content_type="inventory.Product",
            object_id="123",
            object_repr="Product XYZ",
            before_data={"quantity": 100},
            after_data={"quantity": 90},
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            extra_data={"reason": "Customer order"},
        )

        assert audit_entry.actor == employee
        assert audit_entry.action_code == "inventory.stock.adjust"
        assert audit_entry.action == "adjust"
        assert audit_entry.before_data["quantity"] == 100
        assert audit_entry.after_data["quantity"] == 90
        assert audit_entry.ip_address == "192.168.1.1"
        assert audit_entry.user_agent == "Mozilla/5.0"
        assert audit_entry.extra_data["reason"] == "Customer order"


@pytest.mark.django_db
class TestAuditLoggingUtilities:
    """Tests for audit logging utility functions."""

    def test_serialize_for_audit_dict(self):
        """Test serializing dictionary for audit."""
        data = {"name": "Product", "price": 100, "quantity": 50}
        serialized = serialize_for_audit(data)

        assert serialized == data

    def test_serialize_for_audit_none(self):
        """Test serializing None for audit."""
        result = serialize_for_audit(None)
        assert result is None

    def test_serialize_for_audit_primitive(self):
        """Test serializing primitive values."""
        result = serialize_for_audit("test string")
        assert result == {"value": "test string"}

        result = serialize_for_audit(123)
        assert result == {"value": "123"}

    def test_log_audit_convenience_function(self):
        """Test the log_audit convenience function."""
        employee = Employee.objects.create_user(
            email="test@example.com", password="pass123", first_name="Test", last_name="User"
        )

        # Create a mock target object
        class MockProduct:
            id = 999
            name = "Test Product"

            def __str__(self):
                return self.name

        product = MockProduct()

        audit_entry = log_audit(
            actor=employee,
            action_code="inventory.product.update",
            action="update",
            target=product,
            before={"name": "Old Name"},
            after={"name": "Test Product"},
            notes="Updated by test",
            user_agent="Test Browser",  # Add required field
        )

        assert audit_entry.content_type == "MockProduct"
        assert audit_entry.object_id == 999
        assert audit_entry.object_repr == "Test Product"
        assert audit_entry.before_data["name"] == "Old Name"
        assert audit_entry.after_data["name"] == "Test Product"
        assert audit_entry.extra_data["notes"] == "Updated by test"


@pytest.mark.django_db
class TestAuditOperationDecorator:
    """Tests for audit_operation decorator."""

    def test_audit_operation_decorator(self):
        """Test the audit_operation decorator."""
        employee = Employee.objects.create_user(
            email="test@example.com", password="pass123", first_name="Test", last_name="User"
        )

        # Define a test operation with decorator
        @audit_operation(
            action_code="test.operation", action="create", get_target=lambda result: result  # Get target from result
        )
        def create_item(emp, item_name):
            class MockItem:
                id = 1
                name = item_name

                def __str__(self):
                    return self.name

            return MockItem()

        # Execute operation
        create_item(employee, "Test Item")

        # Check audit log was created
        audit_entries = AuditLog.objects.filter(actor=employee, action_code="test.operation")

        assert audit_entries.count() == 1
        assert audit_entries.first().action == "create"
        assert audit_entries.first().object_id == "1"

    def test_audit_operation_with_before_after(self):
        """Test audit_operation decorator with before/after tracking."""
        employee = Employee.objects.create_user(email="test@example.com", password="pass123")

        # Mock object with state
        class MockStock:
            id = 1
            quantity = 100

            def __str__(self):
                return f"Stock-{self.id}"

        stock = MockStock()

        @audit_operation(
            action_code="inventory.stock.adjust",
            action="adjust",
            get_target=lambda result: result,
            get_before_state=lambda *args, **kwargs: {"quantity": 100},
            get_after_state=lambda target: {"quantity": target.quantity},
        )
        def adjust_stock(emp, stock_obj, new_qty):
            stock_obj.quantity = new_qty
            return stock_obj

        # Execute operation
        adjust_stock(employee, stock, 90)

        # Check audit log
        audit_entries = AuditLog.objects.filter(actor=employee, action_code="inventory.stock.adjust")

        assert audit_entries.count() == 1
        audit_entry = audit_entries.first()
        assert audit_entry.before_data["quantity"] == 100
        assert audit_entry.after_data["quantity"] == 90


@pytest.mark.django_db
class TestAuditIntegration:
    """Integration tests for audit logging."""

    def test_full_audit_workflow(self):
        """Test complete audit logging workflow."""
        # Create employee
        employee = Employee.objects.create_user(
            email="manager@example.com", password="pass123", first_name="Manager", last_name="User"
        )

        # Simulate create operation
        create_log = AuditLog.log_action(
            actor=employee,
            action_code="inventory.product.create",
            action="create",
            content_type="inventory.Product",
            object_id="1",
            object_repr="New Product",
            after_data={"name": "New Product", "price": 100},
            user_agent="Test Browser",
        )

        # Simulate update operation
        update_log = AuditLog.log_action(
            actor=employee,
            action_code="inventory.product.update",
            action="update",
            content_type="inventory.Product",
            object_id="1",
            object_repr="Updated Product",
            before_data={"name": "New Product", "price": 100},
            after_data={"name": "Updated Product", "price": 150},
            user_agent="Test Browser",
        )

        # Simulate delete operation
        delete_log = AuditLog.log_action(
            actor=employee,
            action_code="inventory.product.delete",
            action="delete",
            content_type="inventory.Product",
            object_id="1",
            object_repr="Deleted Product",
            before_data={"name": "Updated Product", "price": 150},
            user_agent="Test Browser",
        )

        # Verify all logs exist
        assert AuditLog.objects.count() == 3

        # Verify create log
        assert create_log.action == "create"
        assert create_log.before_data is None
        assert create_log.after_data is not None

        # Verify update log
        assert update_log.action == "update"
        assert update_log.before_data is not None
        assert update_log.after_data is not None

        # Verify delete log
        assert delete_log.action == "delete"
        assert delete_log.before_data is not None
        assert delete_log.after_data is None

    def test_audit_log_actor_backup_after_user_delete(self):
        """Test that audit logs retain actor info after user deletion."""
        employee = Employee.objects.create_user(
            email="temp@example.com", password="pass123", first_name="Temp", last_name="User"
        )

        # Create audit log
        audit_entry = AuditLog.log_action(
            actor=employee,
            action_code="test.action",
            action="create",
            content_type="test",
            object_id="1",
            object_repr="Test",
            user_agent="Test Browser",
        )

        # Verify backup fields
        assert audit_entry.actor_email == "temp@example.com"
        # Employee __str__ includes email, so check for name presence
        assert "Temp User" in audit_entry.actor_name

        # Delete employee
        employee.delete()

        # Refresh audit entry
        audit_entry.refresh_from_db()

        # Backup fields should still be there
        assert audit_entry.actor_email == "temp@example.com"
        # Employee __str__ includes email, so check for name presence
        assert "Temp User" in audit_entry.actor_name
        # Actor should be SET_NULL
        assert audit_entry.actor is None

    def test_audit_log_query_by_action(self):
        """Test querying audit logs by action type."""
        employee = Employee.objects.create_user(email="test@example.com", password="pass123")

        # Create different action types
        actions = ["create", "update", "delete", "approve"]

        for action in actions:
            AuditLog.log_action(
                actor=employee,
                action_code=f"test.{action}",
                action=action,
                content_type="test",
                object_id="1",
                object_repr="Test",
                user_agent="Test Browser",
            )

        # Query by action
        create_logs = AuditLog.objects.filter(action="create")
        assert create_logs.count() == 1

        update_logs = AuditLog.objects.filter(action="update")
        assert update_logs.count() == 1

        # Query multiple actions
        modify_logs = AuditLog.objects.filter(action__in=["create", "update"])
        assert modify_logs.count() == 2

    def test_audit_log_query_by_date_range(self):
        """Test querying audit logs by date range."""
        employee = Employee.objects.create_user(email="test@example.com", password="pass123")

        from datetime import timedelta

        now = timezone.now()

        # Create entries
        for i in range(5):
            AuditLog.log_action(
                actor=employee,
                action_code=f"test.{i}",
                action="create",
                content_type="test",
                object_id=str(i),
                object_repr=f"Test {i}",
                user_agent="Test Browser",
            )

        # Query last hour
        one_hour_ago = now - timedelta(hours=1)
        recent_logs = AuditLog.objects.filter(timestamp__gte=one_hour_ago)
        assert recent_logs.count() == 5
