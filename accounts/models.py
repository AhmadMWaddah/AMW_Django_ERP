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
from django.utils.text import slugify


class EmployeeManager(BaseUserManager):
    """
    Custom manager for Employee model.
    Provides create_user and create_superuser methods.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular Employee user.

        Email is normalized to lowercase for case-insensitive authentication.
        """
        if not email:
            raise ValueError("Email address is required")

        # Normalize email to lowercase (both local and domain parts)
        # Django's normalize_email() only lowercases the domain part
        email = email.lower()

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

    # -- Slug Field --
    slug = models.SlugField(
        "Slug",
        max_length=150,
        unique=True,
        blank=True,
        help_text="URL-friendly identifier. Auto-generated from name or email.",
    )

    # -- Timestamps --
    date_joined = models.DateTimeField(
        "Date Joined", default=timezone.now, help_text="Date/time when the employee account was created."
    )

    # -- Manager --
    objects = EmployeeManager()

    # -- IAM Integration (Constitution Section 6.3) --
    department = models.ForeignKey(
        "security.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        help_text="Department this employee belongs to",
    )
    roles = models.ManyToManyField(
        "security.Role", blank=True, related_name="employees", help_text="Roles assigned to this employee"
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

    def _generate_slug(self):
        """Generate a unique slug from name or email."""
        if self.first_name and self.last_name:
            base_slug = slugify(f"{self.first_name}-{self.last_name}")
        else:
            base_slug = slugify(self.email.split("@")[0])

        if not base_slug:
            base_slug = slugify(self.email.replace("@", "-").replace(".", "-"))

        slug = base_slug
        counter = 1
        while Employee.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = slug

    def save(self, *args, **kwargs):
        """Auto-generate slug if not set."""
        if not self.slug:
            self._generate_slug()
        super().save(*args, **kwargs)
