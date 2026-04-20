import pytest


@pytest.mark.unit
@pytest.mark.django_db
class TestReportJobModel:
    """Unit tests for ReportJob model."""

    @pytest.fixture
    def setup_employee(self):
        """Create test employee."""
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="reporter@amw.io",
            password="test123",
            first_name="Report",
            last_name="User",
        )

    def test_report_job_creation(self, setup_employee):
        """Test creating a report job."""
        from reporting.models import ReportJob

        job = ReportJob.objects.create(
            actor=setup_employee,
            report_type=ReportJob.ReportType.INVENTORY_VALUATION,
        )

        assert job.id is not None
        assert job.status == ReportJob.Status.PENDING
        assert job.report_type == ReportJob.ReportType.INVENTORY_VALUATION
        assert job.actor == setup_employee

    def test_report_job_str(self, setup_employee):
        """Test string representation."""
        from reporting.models import ReportJob

        job = ReportJob.objects.create(
            actor=setup_employee,
            report_type=ReportJob.ReportType.SALES_SUMMARY,
        )

        assert "sales_summary" in str(job)
        assert "pending" in str(job)

    def test_report_job_status_choices(self, setup_employee):
        """Test status choices."""
        from reporting.models import ReportJob

        job = ReportJob.objects.create(
            actor=setup_employee,
            report_type=ReportJob.ReportType.STOCK_MOVEMENT,
            status=ReportJob.Status.PROCESSING,
        )

        assert job.status == ReportJob.Status.PROCESSING
        assert job.get_status_display() == "Processing"

    def test_report_job_report_type_choices(self, setup_employee):
        """Test report type choices."""
        from reporting.models import ReportJob

        for report_type in ReportJob.ReportType.values:
            job = ReportJob.objects.create(
                actor=setup_employee,
                report_type=report_type,
            )
            assert job.report_type == report_type

        assert ReportJob.ReportType.INVENTORY_VALUATION == "inventory_valuation"
        assert ReportJob.ReportType.SALES_SUMMARY == "sales_summary"
        assert ReportJob.ReportType.STOCK_MOVEMENT == "stock_movement"

    def test_report_job_pending_default(self, setup_employee):
        """Test default status is pending."""
        from reporting.models import ReportJob

        job = ReportJob.objects.create(
            actor=setup_employee,
            report_type=ReportJob.ReportType.INVENTORY_VALUATION,
        )

        assert job.status == ReportJob.Status.PENDING

    def test_report_job_error_message(self, setup_employee):
        """Test error message storage."""
        from reporting.models import ReportJob

        job = ReportJob.objects.create(
            actor=setup_employee,
            report_type=ReportJob.ReportType.INVENTORY_VALUATION,
            status=ReportJob.Status.FAILED,
            error_message="Connection timeout",
        )

        assert job.error_message == "Connection timeout"


@pytest.mark.unit
@pytest.mark.django_db
class TestCeleryTaskIntegration:
    """Unit tests for Celery task integration."""

    @pytest.fixture
    def setup_employee(self):
        """Create test employee."""
        from accounts.models import Employee

        return Employee.objects.create_user(
            email="reporter@amw.io",
            password="test123",
            first_name="Report",
            last_name="User",
        )

    def test_task_can_be_imported(self, setup_employee):
        """Test that Celery tasks can be imported."""
        from reporting.tasks import (
            generate_inventory_valuation_report,
            generate_sales_summary_report,
            generate_stock_movement_report,
        )

        assert callable(generate_inventory_valuation_report)
        assert callable(generate_sales_summary_report)
        assert callable(generate_stock_movement_report)

    def test_task_has_retry_config(self, setup_employee):
        """Test tasks have retry configuration."""
        from reporting.tasks import generate_inventory_valuation_report

        assert generate_inventory_valuation_report.max_retries == 3
        assert generate_inventory_valuation_report.default_retry_delay == 60
