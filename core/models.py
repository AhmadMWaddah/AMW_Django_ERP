"""
-- AMW Django ERP - Core Models --

This module contains base models and mixins used across the project.

Constitution Alignment:
- Section 6.4: Soft Delete Rule
- Section 6.7: Audit Rule
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating created/modified fields.

    All models should inherit from this to ensure consistent timestamp tracking.
    """

    created_at = models.DateTimeField(auto_now_add=True, help_text="Date/time when the record was created")
    modified_at = models.DateTimeField(auto_now=True, help_text="Date/time when the record was last modified")

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Custom manager that excludes soft-deleted records by default.
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        """Return all records including soft-deleted ones."""
        return super().get_queryset()

    def deleted_only(self):
        """Return only soft-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract base model that provides soft delete functionality.

    Constitution Section 6.4: Soft delete is the default for core business entities.

    Usage:
        class Product(SoftDeleteModel):
            name = models.CharField(max_length=255)

        # Soft delete
        product.delete()

        # Restore
        product.undelete()

        # Check if deleted
        product.is_deleted
    """

    deleted_at = models.DateTimeField(null=True, blank=True, help_text="Date/time when the record was soft-deleted")

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the record by setting deleted_at timestamp.
        Actual deletion can be performed using hard_delete() if needed.
        """
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the record from the database.
        Use with caution - this bypasses the soft delete mechanism.
        """
        super().delete(using=using, keep_parents=keep_parents)

    def undelete(self):
        """
        Restore a soft-deleted record by clearing deleted_at.
        """
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self):
        """Check if the record is soft-deleted."""
        return self.deleted_at is not None


class UUIDPrimaryKeyModel(models.Model):
    """
    Abstract base model that provides UUID as primary key.

    Use this for models where predictable integer IDs are a security concern.
    """

    id = models.UUIDField(primary_key=True, editable=False)

    class Meta:
        abstract = True
