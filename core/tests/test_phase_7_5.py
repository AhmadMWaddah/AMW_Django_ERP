"""
Phase 7.5 Tests: Pagination utility and detail views.
"""

from django.test import TestCase
from django.urls import reverse

from accounts.models import Employee
from audit.models import AuditLog
from inventory.models import Category, Product
from sales.models import Customer, CustomerCategory
from security.models import Department, Policy, Role


class TestPaginationUtility(TestCase):
    """Test the core.utils.paginate_queryset utility."""

    def setUp(self):
        """Create test data."""
        # Create Employee for audit logs
        self.employee = Employee.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )

        # Create categories for pagination testing
        for i in range(25):
            Category.objects.create(name=f"Category {i}")

    def test_pagination_default_page_size(self):
        """Test default 20-item page size."""
        from core.utils import paginate_queryset

        queryset = Category.objects.all()
        request = self.client.get("/categories/").wsgi_request
        result = paginate_queryset(queryset, request)

        self.assertEqual(len(result["page_obj"].object_list), 20)
        self.assertEqual(result["total_items"], 25)
        self.assertEqual(result["total_pages"], 2)
        self.assertTrue(result["has_next"])
        self.assertFalse(result["has_previous"])

    def test_pagination_second_page(self):
        """Test pagination to second page."""
        from core.utils import paginate_queryset

        queryset = Category.objects.all()
        request = self.client.get("/categories/?page=2").wsgi_request
        result = paginate_queryset(queryset, request)

        self.assertEqual(len(result["page_obj"].object_list), 5)
        self.assertEqual(result["page_obj"].number, 2)
        self.assertFalse(result["has_next"])
        self.assertTrue(result["has_previous"])

    def test_pagination_invalid_page(self):
        """Test pagination with invalid page number defaults to page 1."""
        from core.utils import paginate_queryset

        queryset = Category.objects.all()
        request = self.client.get("/categories/?page=invalid").wsgi_request
        result = paginate_queryset(queryset, request)

        self.assertEqual(result["page_obj"].number, 1)

    def test_pagination_out_of_range(self):
        """Test pagination with out-of-range page returns last page."""
        from core.utils import paginate_queryset

        queryset = Category.objects.all()
        request = self.client.get("/categories/?page=999").wsgi_request
        result = paginate_queryset(queryset, request)

        self.assertEqual(result["page_obj"].number, 2)


class TestAuditLogViews(TestCase):
    """Test Audit Log list and detail views."""

    def setUp(self):
        """Create test employee with audit view permission and audit logs."""
        department = Department.objects.create(name="Finance")
        policy = Policy.objects.create(
            name="Audit: View",
            resource="audit.*",
            action="view",
            effect="allow",
        )
        role = Role.objects.create(name="Auditor", department=department)
        role.policies.add(policy)

        self.employee = Employee.objects.create_user(
            email="auditor@example.com",
            first_name="Audit",
            last_name="User",
            password="testpass123",
        )
        self.employee.roles.add(role)
        self.client.force_login(self.employee)

        # Create audit logs
        for i in range(25):
            AuditLog.objects.create(
                actor=self.employee,
                action="update" if i % 2 == 0 else "create",
                action_code=f"test.action.{i}",
                content_type="inventory.Product",
                object_id=str(i),
                object_repr=f"Product {i}",
                before_data={"quantity": i} if i % 2 == 0 else None,
                after_data={"quantity": i + 10},
            )

    def test_audit_log_list_returns_success(self):
        """Test audit log list view returns success status."""
        response = self.client.get(reverse("audit:AuditLogList"))
        self.assertEqual(response.status_code, 200)

    def test_audit_log_list_pagination_context(self):
        """Test audit log list includes pagination context."""
        response = self.client.get(reverse("audit:AuditLogList"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
        self.assertEqual(len(response.context["logs"]), 20)

    def test_audit_log_list_search_context(self):
        """Test audit log search returns filtered context."""
        response = self.client.get(reverse("audit:AuditLogList"), {"q": "Product 5"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_items"], 1)

    def test_audit_log_list_action_filter_context(self):
        """Test audit log action filter returns filtered context."""
        response = self.client.get(reverse("audit:AuditLogList"), {"action": "create"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_items"], 12)

    def test_audit_log_detail_returns_success(self):
        """Test audit log detail view returns success status."""
        log = AuditLog.objects.first()
        response = self.client.get(reverse("audit:AuditLogDetail", args=[log.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["log"], log)


class TestSecurityDetailViews(TestCase):
    """Test Security module detail views."""

    def setUp(self):
        """Create test employee, department, role, and policies."""
        self.employee = Employee.objects.create_user(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="testpass123",
        )

        self.department = Department.objects.create(name="IT Department")
        self.child_dept = Department.objects.create(name="Backend Team", parent=self.department)

        self.policy = Policy.objects.create(
            name="inventory.adjust",
            resource="inventory.*",
            action="adjust",
            effect="allow",
        )
        dept_view_policy = Policy.objects.create(
            name="Dept View", resource="security.department", action="view", effect="allow"
        )
        role_view_policy = Policy.objects.create(
            name="Role View", resource="security.role", action="view", effect="allow"
        )
        policy_view_policy = Policy.objects.create(
            name="Policy View", resource="security.policy", action="view", effect="allow"
        )

        self.role = Role.objects.create(name="Warehouse Staff", department=self.department)
        self.role.policies.add(self.policy, dept_view_policy, role_view_policy, policy_view_policy)
        self.employee.roles.add(self.role)
        self.employee.save()

        self.client.force_login(self.employee)

    def test_department_detail_returns_success(self):
        """Test department detail view returns success status."""
        response = self.client.get(reverse("Security:DepartmentDetail", args=[self.department.slug]))
        self.assertEqual(response.status_code, 200)

    def test_role_detail_returns_success(self):
        """Test role detail view returns success status."""
        response = self.client.get(reverse("Security:RoleDetail", args=[self.role.slug]))
        self.assertEqual(response.status_code, 200)

    def test_policy_detail_returns_success(self):
        """Test policy detail view returns success status."""
        response = self.client.get(reverse("Security:PolicyDetail", args=[self.policy.slug]))
        self.assertEqual(response.status_code, 200)


class TestEmployeeDetailView(TestCase):
    """Test Employee detail/profile view."""

    def setUp(self):
        """Create test employee."""
        self.admin = Employee.objects.create_user(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="testpass123",
        )
        self.employee = Employee.objects.create_user(
            email="employee@example.com",
            first_name="John",
            last_name="Doe",
            password="testpass123",
        )
        self.client.force_login(self.admin)

    def test_employee_detail_returns_success(self):
        """Test employee detail view returns success status."""
        response = self.client.get(reverse("Accounts:EmployeeDetail", args=[self.employee.slug]))
        self.assertEqual(response.status_code, 200)


class TestListViewsPagination(TestCase):
    """Test that all list views have pagination applied."""

    def setUp(self):
        """Create test employee with view permissions and login."""
        department = Department.objects.create(name="General")
        policies = [
            Policy.objects.create(name="Inventory: View", resource="inventory.*", action="view", effect="allow"),
            Policy.objects.create(name="Customer: View", resource="customer.*", action="view", effect="allow"),
            Policy.objects.create(name="Sales: View", resource="sales.*", action="view", effect="allow"),
            Policy.objects.create(name="Dept: View", resource="security.department", action="view", effect="allow"),
            Policy.objects.create(name="Role: View", resource="security.role", action="view", effect="allow"),
            Policy.objects.create(name="Policy: View", resource="security.policy", action="view", effect="allow"),
        ]
        role = Role.objects.create(name="Viewer", department=department)
        role.policies.add(*policies)

        self.employee = Employee.objects.create_user(
            email="viewer@example.com",
            first_name="Viewer",
            last_name="User",
            password="testpass123",
        )
        self.employee.roles.add(role)
        self.client.force_login(self.employee)

        # Create test data
        self.category = Category.objects.create(name="Test Category")
        for i in range(5):
            Product.objects.create(
                name=f"Product {i}",
                sku=f"PROD-{i}",
                category=self.category,
            )

    def test_product_list_has_pagination(self):
        """Test product list view includes pagination context."""
        response = self.client.get(reverse("Inventory:ProductList"))
        self.assertEqual(response.status_code, 200)
        # Check pagination utility was called
        self.assertIn("page_obj", response.context)
        self.assertIn("total_items", response.context)

    def test_category_list_has_pagination(self):
        """Test category list view includes pagination context."""
        response = self.client.get(reverse("Inventory:CategoryList"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)

    def test_customer_list_has_pagination(self):
        """Test customer list view includes pagination context."""
        cat = CustomerCategory.objects.create(name="Retail")
        for i in range(5):
            Customer.objects.create(name=f"Customer {i}", category=cat)

        response = self.client.get(reverse("Sales:CustomerList"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)

    def test_order_list_has_pagination(self):
        """Test order list view includes pagination context."""
        response = self.client.get(reverse("Sales:OrderList"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)

    def test_employee_list_has_pagination(self):
        """Test employee list view includes pagination context."""
        response = self.client.get(reverse("Accounts:EmployeeList"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)

    def test_department_list_has_pagination(self):
        """Test department list view includes pagination context."""
        response = self.client.get(reverse("Security:DepartmentList"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)

    def test_role_list_has_pagination(self):
        """Test role list view includes pagination context."""
        dept = Department.objects.create(name="Test Dept")
        for i in range(5):
            Role.objects.create(name=f"Role {i}", department=dept)

        response = self.client.get(reverse("Security:RoleList"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)

    def test_policy_list_has_pagination(self):
        """Test policy list view includes pagination context."""
        response = self.client.get(reverse("Security:PolicyList"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
