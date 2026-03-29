"""
-- AMW Django ERP - Employee Model --

Constitution Section 6.2: Identity Anchor
- Custom Employee model extending AbstractBaseUser
- Email is the unique identifier (username field)
- Foundation for IAM: Employee -> Department -> Role -> Policies

Fields:
- email: Unique identifier for login
- first_name, last_name: Employee identity
- is_active: Account status
- is_staff: Admin access
- date_joined: Timestamp
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class EmployeeManager(BaseUserManager):
    """
    Custom manager for Employee model.
    Provides create_user and create_superuser methods.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular Employee user."""
        if not email:
            raise ValueError("Email address is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser (admin)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class Employee(AbstractBaseUser, PermissionsMixin):
    """
    Custom Employee model - the identity anchor for AMW Django ERP.

    Replaces the default Django User model with email-based authentication.
    """

    # -- Identity Fields --
    email = models.EmailField("Email Address", unique=True, help_text="Required. Email address used for login.")
    first_name = models.CharField(
        "First Name", max_length=30, blank=True, help_text="Optional. First name of the employee."
    )
    last_name = models.CharField(
        "Last Name", max_length=30, blank=True, help_text="Optional. Last name of the employee."
    )

    # -- Status Fields --
    is_active = models.BooleanField(
        "Active", default=True, help_text="Designates whether this employee account is active."
    )
    is_staff = models.BooleanField(
        "Staff Status", default=False, help_text="Designates whether the employee can log into admin."
    )

    # -- Timestamps --
    date_joined = models.DateTimeField(
        "Date Joined", default=timezone.now, help_text="Date/time when the employee account was created."
    )

    # -- Manager --
    objects = EmployeeManager()
    
    # -- IAM Integration (Constitution Section 6.3) --
    department = models.ForeignKey(
        'security.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text='Department this employee belongs to'
    )
    roles = models.ManyToManyField(
        'security.Role',
        blank=True,
        related_name='employees',
        help_text='Roles assigned to this employee'
    )
    
    # -- Required for AbstractBaseUser --
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # -- Meta --
    class Meta:
        db_table = "employees"
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ["email"]

    # -- String Representation --
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.email})"
        return self.email

    def get_full_name(self):
        """Return the full name of the employee."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    def get_short_name(self):
        """Return the short name of the employee (first name or email)."""
        return self.first_name if self.first_name else self.email
