"""
-- AMW Django ERP - Reporting Models --

Models for tracking asynchronous report generation jobs.

Constitution Alignment:
- Section 15.8: Reporting must align with Architecture targets
- Audit logs remain the source of truth for historical reports

Models:
- ReportJob: Tracks background report generation status
"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class ReportJob(TimeStampedModel):
    """
    Tracks asynchronous report generation jobs.

    Used by Celery tasks to generate inventory valuation,
    sales summaries, and other heavy reports.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class ReportType(models.TextChoices):
        INVENTORY_VALUATION = "inventory_valuation", "Inventory Valuation"
        SALES_SUMMARY = "sales_summary", "Sales Summary"
        STOCK_MOVEMENT = "stock_movement", "Stock Movement"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="report_jobs",
        help_text="User who requested the report",
    )
    report_type = models.CharField(
        max_length=50,
        choices=ReportType.choices,
        help_text="Type of report to generate",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current status of the report job",
    )
    result_file = models.FileField(
        upload_to="reports/",
        blank=True,
        null=True,
        help_text="Generated report file (CSV/PDF)",
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Error message if job failed",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["actor", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.report_type} - {self.status} ({self.created_at})"
