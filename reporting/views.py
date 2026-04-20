"""
-- AMW Django ERP - Reporting Views --

HTMX-enabled views for report generation.

Constitution Alignment:
- Section 15.8: Reporting must align with Architecture targets
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from security.logic.enforcement import require_permission


@login_required
@require_permission("reporting.reportjob", "view")
def report_list(request):
    """
    Display list of report jobs for the current user.
    """
    from reporting.models import ReportJob

    jobs = ReportJob.objects.filter(actor=request.user)[:20]
    return render(request, "reporting/report_list.html", {"jobs": jobs})


@login_required
@require_http_methods(["POST"])
@require_permission("reporting.reportjob", "add")
def request_report(request):
    """
    Request a new background report generation.

    Expects POST data:
    - report_type: Type of report (inventory_valuation, sales_summary, stock_movement)
    """
    from reporting.models import ReportJob

    report_type = request.POST.get("report_type")

    if report_type not in ReportJob.ReportType.values:
        return JsonResponse(
            {"error": "Invalid report type"},
            status=400,
        )

    job = ReportJob.objects.create(
        actor=request.user,
        report_type=report_type,
    )

    if report_type == ReportJob.ReportType.INVENTORY_VALUATION:
        from reporting.tasks import generate_inventory_valuation_report

        generate_inventory_valuation_report.delay(job.id)
    elif report_type == ReportJob.ReportType.SALES_SUMMARY:
        from reporting.tasks import generate_sales_summary_report

        generate_sales_summary_report.delay(job.id)
    elif report_type == ReportJob.ReportType.STOCK_MOVEMENT:
        from reporting.tasks import generate_stock_movement_report

        generate_stock_movement_report.delay(job.id)

    messages.success(request, f"Report requested: {job.get_report_type_display()}")

    if request.htmx:
        return JsonResponse({"message": f"Report requested: {job.get_report_type_display()}"})

    return JsonResponse({"job_id": job.id, "status": job.status})
