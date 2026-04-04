"""
-- AMW Django ERP - Security/IAM Tests --

Comprehensive test suite for IAM (Identity and Access Management).

Tests cover:
- Department hierarchy and relationships
- Policy creation and matching with wildcards
- Role management and policy assignments
- PolicyEngine permission checking
- Employee integration with IAM
"""

import pytest
from django.db import IntegrityError

from accounts.models import Employee
from security.logic.enforcement import PolicyEngine, check_permission
from security.models import Department, Policy, Role


@pytest.mark.django_db
class TestDepartmentModel:
    """Tests for Department model."""

    def test_create_department(self):
        """Test creating a department."""
        dept = Department.objects.create(name="Information Technology", description="IT department")

        assert dept.name == "Information Technology"
        assert dept.slug == "information-technology"
        assert dept.parent is None
        assert dept.is_active is True

    def test_department_auto_slug(self):
        """Test that department code is auto-generated from name."""
        dept = Department.objects.create(name="Human Resources")
        assert dept.slug == "human-resources"

    def test_department_custom_slug(self):
        """Test that custom department code is preserved."""
        dept = Department.objects.create(name="Research and Development", slug="rnd")
        assert dept.slug == "rnd"

    def test_department_hierarchy(self):
        """Test parent-child department relationships."""
        # Create parent
        it_dept = Department.objects.create(name="IT")

        # Create children
        backend = Department.objects.create(name="Backend", parent=it_dept)
        frontend = Department.objects.create(name="Frontend", parent=it_dept)

        assert backend.parent == it_dept
        assert frontend.parent == it_dept
        assert it_dept.children.count() == 2

    def test_department_get_all_children(self):
        """Test recursive retrieval of all descendant departments."""
        # Create hierarchy: IT -> Backend -> API
        it_dept = Department.objects.create(name="IT")
        backend = Department.objects.create(name="Backend", parent=it_dept)
        api = Department.objects.create(name="API", parent=backend)

        # Get all children
        all_children = it_dept.get_all_children()

        assert len(all_children) == 2  # backend and api
        assert backend in all_children
        assert api in all_children

    def test_department_str_representation(self):
        """Test department string representation."""
        dept = Department.objects.create(name="Sales")
        assert str(dept) == "Sales"

    def test_department_unique_name(self):
        """Test that department names must be unique."""
        Department.objects.create(name="Marketing")

        with pytest.raises(IntegrityError):
            Department.objects.create(name="Marketing")


@pytest.mark.django_db
class TestPolicyModel:
    """Tests for Policy model."""

    def test_create_policy(self):
        """Test creating a policy."""
        policy = Policy.objects.create(
            name="Stock Adjustment", resource="inventory.stock", action="adjust", effect="allow"
        )

        assert policy.name == "Stock Adjustment"
        assert policy.slug == "stock-adjustment"
        assert policy.resource == "inventory.stock"
        assert policy.action == "adjust"
        assert policy.effect == "allow"

    def test_policy_auto_slug(self):
        """Test that policy code is auto-generated."""
        policy = Policy.objects.create(name="Create Sales Order", resource="sales.order", action="create")
        assert policy.slug == "create-sales-order"

    def test_policy_deny_effect(self):
        """Test creating a deny policy."""
        policy = Policy.objects.create(
            name="Delete Products", resource="inventory.product", action="delete", effect="deny"
        )
        assert policy.effect == "deny"

    def test_policy_matches_exact(self):
        """Test policy matching with exact values."""
        policy = Policy.objects.create(name="Stock Adjust", resource="inventory.stock", action="adjust")

        assert policy.matches("inventory.stock", "adjust") is True
        assert policy.matches("inventory.stock", "create") is False
        assert policy.matches("inventory.product", "adjust") is False

    def test_policy_matches_wildcard_resource(self):
        """Test policy matching with wildcard in resource."""
        policy = Policy.objects.create(name="All Inventory", resource="inventory.*", action="*")

        assert policy.matches("inventory.stock", "adjust") is True
        assert policy.matches("inventory.product", "create") is True
        assert policy.matches("sales.order", "create") is False

    def test_policy_matches_wildcard_action(self):
        """Test policy matching with wildcard in action."""
        policy = Policy.objects.create(name="Stock All Actions", resource="inventory.stock", action="*")

        assert policy.matches("inventory.stock", "adjust") is True
        assert policy.matches("inventory.stock", "create") is True
        assert policy.matches("inventory.stock", "delete") is True
        assert policy.matches("inventory.product", "adjust") is False

    def test_policy_matches_complex_pattern(self):
        """Test policy matching with complex wildcard patterns."""
        policy = Policy.objects.create(name="Sales Read Only", resource="sales.*", action="read")

        assert policy.matches("sales.order", "read") is True
        assert policy.matches("sales.customer", "read") is True
        assert policy.matches("sales.order", "create") is False

    def test_policy_str_representation(self):
        """Test policy string representation."""
        policy = Policy.objects.create(name="Test Policy", resource="test", action="read", effect="allow")
        assert str(policy) == "Test Policy (allow)"

    def test_policy_unique_name(self):
        """Test that policy names must be unique."""
        Policy.objects.create(name="Unique Policy", resource="test", action="read")

        with pytest.raises(IntegrityError):
            Policy.objects.create(name="Unique Policy", resource="test2", action="write")


@pytest.mark.django_db
class TestRoleModel:
    """Tests for Role model."""

    def test_create_role(self):
        """Test creating a role."""
        dept = Department.objects.create(name="IT")
        role = Role.objects.create(name="Developer", department=dept, description="Software developer role")

        assert role.name == "Developer"
        assert role.slug == "developer"
        assert role.department == dept
        assert role.is_active is True

    def test_role_unique_in_department(self):
        """Test that role names are unique within department."""
        dept = Department.objects.create(name="Sales")
        Role.objects.create(name="Manager", department=dept)

        with pytest.raises(IntegrityError):
            Role.objects.create(name="Manager", department=dept)

    def test_role_same_name_different_departments(self):
        """Test that same role name can exist in different departments."""
        it_dept = Department.objects.create(name="IT")
        sales_dept = Department.objects.create(name="Sales")

        it_manager = Role.objects.create(name="Manager", department=it_dept, slug="it-manager")
        sales_manager = Role.objects.create(name="Manager", department=sales_dept, slug="sales-manager")

        assert it_manager != sales_manager
        assert it_manager.department != sales_manager.department

    def test_role_add_policies(self):
        """Test adding policies to a role."""
        dept = Department.objects.create(name="IT")
        role = Role.objects.create(name="Developer", department=dept)

        policy1 = Policy.objects.create(name="Code Commit", resource="git.repository", action="push")
        policy2 = Policy.objects.create(name="Deploy", resource="deployment", action="create")

        role.policies.add(policy1, policy2)

        assert role.policies.count() == 2
        assert policy1 in role.policies.all()
        assert policy2 in role.policies.all()

    def test_role_get_all_policies(self):
        """Test getting all active policies for a role."""
        dept = Department.objects.create(name="IT")
        role = Role.objects.create(name="Admin", department=dept)

        active_policy = Policy.objects.create(name="Active Policy", resource="*", action="*", is_active=True)
        inactive_policy = Policy.objects.create(name="Inactive Policy", resource="test", action="read", is_active=False)

        role.policies.add(active_policy, inactive_policy)

        all_policies = role.get_all_policies()

        assert all_policies.count() == 1
        assert active_policy in all_policies
        assert inactive_policy not in all_policies

    def test_role_str_representation(self):
        """Test role string representation."""
        dept = Department.objects.create(name="HR")
        role = Role.objects.create(name="Recruiter", department=dept)
        assert str(role) == "Recruiter (HR)"


@pytest.mark.django_db
class TestPolicyEngine:
    """Tests for PolicyEngine permission checking."""

    def test_employee_without_roles_has_no_permissions(self):
        """Test that employees without roles have no permissions."""
        dept = Department.objects.create(name="IT")
        employee = Employee.objects.create_user(email="test@example.com", password="pass123", department=dept)

        engine = PolicyEngine(employee)

        assert engine.has_permission("inventory.stock", "adjust") is False
        assert engine.has_permission("sales.order", "create") is False

    def test_employee_with_role_gets_permissions(self):
        """Test that employees get permissions from their role."""
        dept = Department.objects.create(name="IT")
        role = Role.objects.create(name="Developer", department=dept)
        policy = Policy.objects.create(name="Code Access", resource="git.repository", action="push", effect="allow")
        role.policies.add(policy)

        employee = Employee.objects.create_user(email="dev@example.com", password="pass123", department=dept)
        employee.roles.add(role)

        engine = PolicyEngine(employee)

        assert engine.has_permission("git.repository", "push") is True

    def test_deny_policy_overrides_allow(self):
        """Test that deny policies override allow policies."""
        dept = Department.objects.create(name="Sales")
        role = Role.objects.create(name="Sales Rep", department=dept)

        allow_policy = Policy.objects.create(name="Allow Read", resource="sales.*", action="read", effect="allow")
        deny_policy = Policy.objects.create(name="Deny Delete", resource="sales.*", action="delete", effect="deny")

        role.policies.add(allow_policy, deny_policy)

        employee = Employee.objects.create_user(email="sales@example.com", password="pass123", department=dept)
        employee.roles.add(role)

        engine = PolicyEngine(employee)

        # Should be allowed
        assert engine.has_permission("sales.order", "read") is True
        # Should be denied
        assert engine.has_permission("sales.order", "delete") is False

    def test_check_permission_convenience_function(self):
        """Test the check_permission convenience function."""
        dept = Department.objects.create(name="IT")
        role = Role.objects.create(name="Admin", department=dept)
        policy = Policy.objects.create(name="Full Access", resource="*", action="*", effect="allow")
        role.policies.add(policy)

        employee = Employee.objects.create_user(email="admin@example.com", password="pass123", department=dept)
        employee.roles.add(role)

        assert check_permission(employee, "anything", "anything") is True

    def test_policy_engine_with_wildcards(self):
        """Test policy engine with wildcard patterns."""
        dept = Department.objects.create(name="Warehouse")
        role = Role.objects.create(name="Warehouse Manager", department=dept)
        policy = Policy.objects.create(name="Inventory Management", resource="inventory.*", action="*", effect="allow")
        role.policies.add(policy)

        employee = Employee.objects.create_user(email="warehouse@example.com", password="pass123", department=dept)
        employee.roles.add(role)

        engine = PolicyEngine(employee)

        assert engine.has_permission("inventory.stock", "adjust") is True
        assert engine.has_permission("inventory.product", "create") is True
        assert engine.has_permission("inventory.warehouse", "update") is True
        assert engine.has_permission("sales.order", "create") is False

    def test_employee_without_department(self):
        """Test policy engine for employee without department."""
        employee = Employee.objects.create_user(email="noderp@example.com", password="pass123")

        engine = PolicyEngine(employee)
        assert engine.has_permission("anything", "anything") is False


@pytest.mark.django_db
class TestEmployeeIAMIntegration:
    """Tests for Employee model IAM integration."""

    def test_employee_department_assignment(self):
        """Test assigning department to employee."""
        dept = Department.objects.create(name="Marketing")
        employee = Employee.objects.create_user(email="marketing@example.com", password="pass123", department=dept)

        assert employee.department == dept
        assert dept.employees.count() == 1

    def test_employee_multiple_roles(self):
        """Test assigning multiple roles to employee."""
        dept = Department.objects.create(name="IT")

        dev_role = Role.objects.create(name="Developer", department=dept)
        lead_role = Role.objects.create(name="Team Lead", department=dept)

        employee = Employee.objects.create_user(email="lead@example.com", password="pass123", department=dept)
        employee.roles.add(dev_role, lead_role)

        assert employee.roles.count() == 2
        assert dev_role in employee.roles.all()
        assert lead_role in employee.roles.all()

    def test_employee_inherits_role_policies(self):
        """Test that employee inherits policies from all roles."""
        dept = Department.objects.create(name="Operations")

        role1 = Role.objects.create(name="Operator", department=dept)
        role2 = Role.objects.create(name="Supervisor", department=dept)

        policy1 = Policy.objects.create(name="Operate", resource="machine", action="operate")
        policy2 = Policy.objects.create(name="Supervise", resource="machine", action="supervise")

        role1.policies.add(policy1)
        role2.policies.add(policy2)

        employee = Employee.objects.create_user(email="operator@example.com", password="pass123", department=dept)
        employee.roles.add(role1, role2)

        engine = PolicyEngine(employee)

        assert engine.has_permission("machine", "operate") is True
        assert engine.has_permission("machine", "supervise") is True

    def test_employee_department_change_affects_roles(self):
        """Test that changing employee department doesn't break existing roles."""
        dept1 = Department.objects.create(name="IT")
        dept2 = Department.objects.create(name="Sales")

        it_role = Role.objects.create(name="Developer", department=dept1)

        employee = Employee.objects.create_user(email="dev@example.com", password="pass123", department=dept1)
        employee.roles.add(it_role)

        # Change department
        employee.department = dept2
        employee.save()

        # Role should still be assigned
        assert employee.roles.count() == 1
        assert it_role in employee.roles.all()
