# Manual Test Cases — Phase 8: Async Tasks, Reporting & Hardening

**Version:** 1.0 (Phase 8)
**Status:** Ready for testing

---

## Pre-requisites

- Docker services running: `docker-compose up -d`
- Celery worker started: `docker-compose up celery_worker`
- Application running at http://localhost:8010

---

## Report Generation Tests

| Test ID | Description | Expected Result | Status |
|--------|-------------|-----------------|--------|
| RPT-001 | Navigate to Reports page | Reports page loads with sidebar link | ⬜ |
| RPT-002 | View empty report list | "No reports generated yet" message | ⬜ |
| RPT-003 | Select "Inventory Valuation" and click Generate | Report job created, appears in list | ⬜ |
| RPT-004 | Check job status changes to "Processing" | Status shows "Processing" badge | ⬜ |
| RPT-005 | Wait for background task to complete | Status shows "Completed" badge | ⬜ |
| RPT-006 | Click Download on completed report | CSV file downloads | ⬜ |
| RPT-007 | Generate Sales Summary report | Report generates successfully | ⬜ |
| RPT-008 | Generate Stock Movement report | Report generates successfully | ⬜ |

---

## Celery Worker Tests

| Test ID | Description | Expected Result | Status |
|--------|-------------|-----------------|--------|
| CEL-001 | Check Celery worker is running | Worker log shows "ready" | ⬜ |
| CEL-002 | Trigger failed task (disconnect Redis) | Task retries up to 3 times | ⬜ |

---

## Production Settings Tests

| Test ID | Description | Expected Result | Status |
|--------|-------------|-----------------|--------|
| PRD-001 | Run `python manage.py check --deploy` | "System check identified no issues" | ⬜ |
| PRD-002 | Verify DEBUG=False in prod | No debug error pages | ⬜ |
| PRD-003 | Check security headers | X-Frame-Options: DENY in response | ⬜ |

---

## Test Execution Command

```bash
# Start services
docker-compose up -d postgres redis web

# Start Celery worker (in a new terminal)
docker-compose up celery_worker

# Run the manual tests above
# Then verify:
python manage.py check --deploy --settings=config.settings.prod
```

---

## Notes

- Run RPT-003 through RPT-005 sequentially to verify async behavior
- Celery worker must be running for background tasks to execute
- Reports are generated as CSV files in `media/reports/`