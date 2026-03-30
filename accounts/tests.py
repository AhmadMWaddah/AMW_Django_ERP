"""
-- AMW Django ERP - Accounts App Tests --

Test suite for Employee model and authentication flow.

Tests cover:
- Employee model creation and validation
- Email uniqueness constraint
- Superuser creation and permissions
- Login/logout flow
- Security: open redirect protection
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client
from django.urls import reverse

Employee = get_user_model()


@pytest.mark.django_db
class TestEmployeeModel:
    """Tests for the Employee model."""

    def test_create_employee(self):
        """Test creating a regular employee."""
        employee = Employee.objects.create_user(
            email="test@example.com", password="testpass123", first_name="Test", last_name="User"
        )

        assert employee.email == "test@example.com"
        assert employee.first_name == "Test"
        assert employee.last_name == "User"
        assert employee.is_active is True
        assert employee.is_staff is False
        assert employee.is_superuser is False
        assert employee.check_password("testpass123")

    def test_email_uniqueness(self):
        """Test that email must be unique."""
        Employee.objects.create_user(email="duplicate@example.com", password="pass123")

        with pytest.raises(IntegrityError):
            Employee.objects.create_user(email="duplicate@example.com", password="pass456")

    def test_email_normalization(self):
        """Test that email is normalized to lowercase (both local and domain parts).

        AMW Django ERP treats emails as fully case-insensitive.
        EmployeeManager.create_user() normalizes emails to lowercase before saving.
        """
        employee = Employee.objects.create_user(email="TEST@EXAMPLE.COM", password="pass123")

        # Email should be normalized to lowercase by the manager
        # Query from DB to ensure we get the stored value
        from_db = Employee.objects.get(pk=employee.pk)
        assert from_db.email == "test@example.com"

    def test_create_employee_without_email(self):
        """Test that creating employee without email raises error."""
        with pytest.raises(ValueError, match="Email address is required"):
            Employee.objects.create_user(email="", password="pass123")

    def test_string_representation(self):
        """Test employee string representation."""
        # With name
        employee = Employee.objects.create_user(
            email="test@example.com", password="pass123", first_name="John", last_name="Doe"
        )
        assert str(employee) == "John Doe (test@example.com)"

        # Without name
        employee2 = Employee.objects.create_user(email="noname@example.com", password="pass123")
        assert str(employee2) == "noname@example.com"

    def test_get_full_name(self):
        """Test get_full_name method."""
        employee = Employee.objects.create_user(
            email="test@example.com", password="pass123", first_name="Jane", last_name="Smith"
        )
        assert employee.get_full_name() == "Jane Smith"

    def test_get_short_name(self):
        """Test get_short_name method."""
        employee = Employee.objects.create_user(email="test@example.com", password="pass123", first_name="Jane")
        assert employee.get_short_name() == "Jane"

        # Without first name, returns email
        employee2 = Employee.objects.create_user(email="short@example.com", password="pass123")
        assert employee2.get_short_name() == "short@example.com"


@pytest.mark.django_db
class TestSuperuser:
    """Tests for superuser creation."""

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = Employee.objects.create_superuser(
            email="admin@example.com", password="adminpass123", first_name="Admin", last_name="User"
        )

        assert superuser.is_active is True
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.check_password("adminpass123")

    def test_superuser_is_staff(self):
        """Test that superuser must have is_staff=True."""
        with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
            Employee.objects.create_superuser(email="admin2@example.com", password="pass123", is_staff=False)

    def test_superuser_is_superuser(self):
        """Test that superuser must have is_superuser=True."""
        with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
            Employee.objects.create_superuser(email="admin3@example.com", password="pass123", is_superuser=False)


@pytest.mark.django_db
@pytest.mark.integration
class TestAuthenticationFlow:
    """Integration tests for login/logout flow."""

    def setup_method(self):
        """Setup test client."""
        self.client = Client()

    def test_login_page_loads(self):
        """Test that login page loads successfully."""
        response = self.client.get(reverse("Accounts:Login"))
        assert response.status_code == 200
        assert "accounts/pages/login.html" in [t.name for t in response.templates]

    def test_login_success(self):
        """Test successful login."""
        Employee.objects.create_user(email="login@test.com", password="testpass123")

        response = self.client.post(reverse("Accounts:Login"), {"email": "login@test.com", "password": "testpass123"})

        assert response.status_code == 302  # Redirect
        assert response.url == reverse("Accounts:Dashboard")

    @pytest.mark.skip(reason="Django test client recursion bug with template context copying")
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse("Accounts:Login"), {"email": "wrong@test.com", "password": "wrongpass"})

        assert response.status_code == 200  # Stay on login page
        assert "Invalid email or password" in response.content.decode()

    @pytest.mark.skip(reason="Django test client recursion bug with template context copying")
    def test_login_missing_fields(self):
        """Test login with missing email or password."""
        response = self.client.post(reverse("Accounts:Login"), {"email": "", "password": ""})

        assert response.status_code == 200
        assert "Please provide both email and password" in response.content.decode()

    def test_logout(self):
        """Test logout functionality."""
        Employee.objects.create_user(email="logout@test.com", password="testpass123")

        # Login
        self.client.login(username="logout@test.com", password="testpass123")

        # Logout (POST only)
        response = self.client.post(reverse("Accounts:Logout"))

        assert response.status_code == 302
        assert response.url == reverse("Accounts:Login")

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication."""
        response = self.client.get(reverse("Accounts:Dashboard"))

        assert response.status_code == 302  # Redirect to login

    def test_authenticated_user_redirected_from_login(self):
        """Test that authenticated users are redirected from login page."""
        Employee.objects.create_user(email="auth@test.com", password="testpass123")

        self.client.login(username="auth@test.com", password="testpass123")

        response = self.client.get(reverse("Accounts:Login"))

        assert response.status_code == 302
        assert response.url == reverse("Accounts:Dashboard")


@pytest.mark.django_db
@pytest.mark.integration
class TestSecurity:
    """Security tests for authentication views."""

    def setup_method(self):
        """Setup test client."""
        self.client = Client()

    def test_open_redirect_blocked(self):
        """Test that external URLs are blocked in 'next' parameter."""
        Employee.objects.create_user(email="security@test.com", password="testpass123")

        # Try to redirect to external site
        response = self.client.post(
            reverse("Accounts:Login"),
            {"email": "security@test.com", "password": "testpass123", "next": "https://evil.com"},
        )

        # Should redirect to dashboard, not evil.com
        assert response.status_code == 302
        assert response.url == reverse("Accounts:Dashboard")
        assert "evil.com" not in response.url

    def test_protocol_relative_url_blocked(self):
        """Test that protocol-relative URLs are blocked."""
        Employee.objects.create_user(email="security2@test.com", password="testpass123")

        response = self.client.post(
            reverse("Accounts:Login"), {"email": "security2@test.com", "password": "testpass123", "next": "//evil.com"}
        )

        assert response.status_code == 302
        assert response.url == reverse("Accounts:Dashboard")

    def test_safe_relative_url_allowed(self):
        """Test that safe relative URLs are allowed."""
        Employee.objects.create_user(email="security3@test.com", password="testpass123")

        response = self.client.post(
            reverse("Accounts:Login"), {"email": "security3@test.com", "password": "testpass123", "next": "/admin/"}
        )

        assert response.status_code == 302
        assert response.url == "/admin/"

    def test_csrf_protection_on_login(self):
        """Test that login form has CSRF protection."""
        response = self.client.get(reverse("Accounts:Login"))

        assert "csrfmiddlewaretoken" in response.content.decode()

    def test_logout_requires_post(self):
        """Test that logout only accepts POST requests."""
        Employee.objects.create_user(email="logout@test.com", password="testpass123")

        self.client.login(username="logout@test.com", password="testpass123")

        # GET request should fail (405 Method Not Allowed)
        response = self.client.get(reverse("Accounts:Logout"))

        assert response.status_code == 405
