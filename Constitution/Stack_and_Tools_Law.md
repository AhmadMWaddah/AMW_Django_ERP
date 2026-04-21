# Stack & Tools Law - AMW Django ERP

**Extracted from Constitution Section 11**

## 11.1 Technology Stack

| Layer       | Technology                  |
|-------------|-----------------------------|
| Backend     | Python, Django              |
| Database    | PostgreSQL                  |
| Frontend    | HTMX, Django Templates, CSS |
| JS Support  | jQuery only when justified  |
| Async       | Celery + Redis              |
| Testing     | `pytest`, `pytest-django`   |
| Dev Port    | `8010`                      |

## 11.2 Utility Scripts

Official project scripts live in `utils/` and include:

1. `git_task_commit.sh` — Atomic commits with lint check
2. `git_phase_finish.sh` — Phase completion automation
3. `env_factory.sh` — Virtual environment management
4. `test_suite_runner.sh` — Unified testing interface
5. `db_manage_dev.sh` — Database operations
6. `infra_manage.sh` — Docker infrastructure management

### Script Usage

| Utility Script | Usage |
|----------------|-------|
| `git_task_commit.sh` | Atomic commits with lint check |
| `test_suite_runner.sh` | Run tests before committing |
| `db_manage_dev.sh` | Migrations, database operations |
| `infra_manage.sh` | Docker and service management |
| `env_factory.sh` | Initial environment setup |
| `git_phase_finish.sh` | Close a phase to master |

### Mandatory Usage Rule

When working on the project, use the utility scripts where applicable.
For example:
- Database changes: use `./utils/db_manage_dev.sh makemigrations` and `./utils/db_manage_dev.sh migrate`
- Docker/service ops: use `./utils/infra_manage.sh`
- After completing code changes: Orchestrator calls `./utils/git_task_commit.sh`

## 11.3 Script Rule

- Always prefer project utility scripts when they exist and are appropriate for the task.
- If a required script is missing, incomplete, or broken, document the gap.

## 11.4 Environment Rule

- Development setup should remain repeatable.
- Settings should be split clearly by environment.
- Environment-sensitive behavior must be controlled explicitly, not by accidental defaults.
