# AMW Django ERP

**Enterprise Resource Planning System built with Django**

---

## 🎯 Project Overview

AMW Django ERP is a comprehensive, production-ready ERP system designed for real business operations. Built on Django with an operations-first architecture, it covers:

- **Employee Identity & Authentication** - Custom Employee model with policy-based access control
- **Inventory Management** - Stock ledger with Weighted Average Cost (WAC) valuation
- **Sales & CRM** - Customer management and atomic order workflows
- **Purchasing & Procurement** - Supplier workflows and stock receiving
- **Audit Logging** - Complete traceability for all business-critical changes
- **HTMX-Powered Frontend** - Server-rendered, dynamic UI without heavy JavaScript frameworks

---

## 📊 Current Status

| Phase       | Name                                         | Status           | Branch    |
|-------------|----------------------------------------------|------------------|-----------|
| **Phase 1** | Foundation, Automation & Local Scaffolding   | ✅ **COMPLETE**  | `master`  |
| **Phase 2** | Infrastructure & Core Identity               | ✅ **COMPLETE**  | `master`  |
| **Phase 3** | IAM & Security Framework                     | ✅ **COMPLETE**  | `master`  |
| **Phase 4** | Inventory Architecture & Valuation           | ✅ **COMPLETE**  | `master`  |
| **Phase 5** | Sales & CRM Workflows                        | ✅ **COMPLETE**  | `master`  |
| **Phase 6** | Purchasing & Procurement                     | ✅ **COMPLETE**  | `master`  |
| **Phase 7** | Frontend Foundation & HTMX UI                | ✅ **COMPLETE**  | `phase-7` |
| Phase 8     | Async Tasks, Reporting & Hardening           | ⏳ NEXT          | `phase-8` |

**Branch Strategy:**
- `master` - Stable production baseline (Phase 6 complete)
- `phase-3` - Merged to master (v3.0-phase3-complete)
- `phase-4` - Merged to master (v4.0-phase4-complete)
- `phase-5` - Merged to master (v5.0-phase5-complete)
- `phase-6` - Merged to master (v6.0-phase6-complete)
- `phase-7` - Ready for merge (v7.0-phase7-complete pending)
- Future phases will be developed in `phase-X` branches and merged to `master` after approval

**Version Tags:**
- `v3.0-phase3-complete` - IAM & Security Framework
- `v4.0-phase4-complete` - Inventory Architecture & Valuation
- `v5.0-phase5-complete` - Sales & CRM Workflows
- `v6.0-phase6-complete` - Purchasing & Procurement
- `v7.0-phase7-complete` - Frontend Foundation & HTMX UI (pending merge)

**See `Architecture/Phase_7_Frontend_HTMX.md` for Phase 7 completion details.**

**See `Architecture/Phase_5_Sales_CRM.md` for Phase 5 completion details.**

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 15+ (or Docker)
- Redis 7+ (or Docker)

### 1. Clone & Setup

```bash
cd /path/to/AMW_Django_ERP

# Bootstrap git + environment + dependencies
bash utils/env_factory.sh setup

# Activate environment
source .env_amw_dj_erp/bin/activate
```

### 2. Start Infrastructure (Docker)

```bash
# Start PostgreSQL and Redis
bash utils/infra_manage.sh start

# Check services status
bash utils/infra_manage.sh status
```

### 3. Initialize Database

```bash
# Run migrations
bash utils/db_manage_dev.sh migrate

# Create admin superuser
bash utils/db_manage_dev.sh createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver 8010
```

**Access Points:**
- Development Server: http://localhost:8010
- Django Admin: http://localhost:8010/admin/
- Health Check: http://localhost:8010/health/
- PostgreSQL (Docker host port): `localhost:5433`
- Redis (Docker host port): `localhost:6380`

---

## 📁 Project Structure

```
AMW_Django_ERP/
├── Architecture/           # Phase execution plans
│   ├── Phase_1_Foundation.md
│   ├── Phase_2_Infrastructure_Identity.md
│   └── ...
├── Brand/                  # Brand assets and color palette
├── config/                 # Django project configuration
│   └── settings/
│       ├── base.py        # Shared settings
│       ├── dev.py         # Development settings
│       └── prod.py        # Production settings
├── core/                   # Core app (base models, utilities)
├── utils/                  # Utility scripts
│   ├── git_task_commit.sh  # Task-based commits
│   ├── git_phase_finish.sh # Phase merge & tagging automation
│   ├── env_factory.sh      # Environment bootstrap
│   ├── test_suite_runner.sh# Testing & Linting
│   ├── db_manage_dev.sh    # Database operations
│   └── infra_manage.sh     # Docker services
├── templates/              # Global templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User-uploaded media
├── manage.py               # Django CLI
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Tool configuration
├── docker-compose.yml      # Docker services
└── Constitution_AMW_DJ_ERP.md  # Project law
```

---

## 🛠️ Development Tools

Official project utility scripts are located in the `utils/` directory. For detailed documentation and usage examples, refer to the **[Utility Scripts README](utils/README.md)**.

### Utility Scripts

**Git Commits (Multi-Message Format - Constitution Section 9.3):**
```bash
git add path/to/file
bash utils/git_task_commit.sh "Title" "Description"

# Examples:
bash utils/git_task_commit.sh "phase-2: Employee Model" "Added AbstractBaseUser with email auth"
bash utils/git_task_commit.sh "Fix: Navigation bug" "Changed to namespaced URLs accounts:dashboard"
bash utils/git_task_commit.sh "Feature: Open redirect protection" "Added Django's url_has_allowed_host_and_scheme"
```

**Environment Management:**
```bash
bash utils/env_factory.sh setup          # Bootstrap git + venv + dependencies
bash utils/env_factory.sh init-git       # Initialize git repository
bash utils/env_factory.sh create         # Create virtual environment
bash utils/env_factory.sh install        # Install dependencies
```

**Phase Completion & Tagging:**
```bash
bash utils/git_phase_finish.sh <phase-number> [tag]

# Examples:
bash utils/git_phase_finish.sh 2           # Auto-generates tag v2.0-phase2-complete
bash utils/git_phase_finish.sh 2 v2.0     # Custom tag
```

**Testing:**
```bash
bash utils/test_suite_runner.sh          # Run all tests
bash utils/test_suite_runner.sh unit     # Unit tests only
bash utils/test_suite_runner.sh coverage # With coverage
bash utils/test_suite_runner.sh lint     # Run linters
```

# Database operations
bash utils/db_manage_dev.sh migrate
bash utils/db_manage_dev.sh shell
bash utils/db_manage_dev.sh createsuperuser

# Infrastructure (Docker)
bash utils/infra_manage.sh start
bash utils/infra_manage.sh logs
bash utils/infra_manage.sh status
```

### Code Quality

```bash
# Run linters
ruff check .
black --check .

# Format code
black .
ruff check --fix .

# Run tests with coverage
pytest --cov=. --cov-report=html
```

---

## 📋 Key Features

### Architecture Highlights

- **Operations-First Business Logic** - Core workflows in `operations/` modules, not views
- **Soft Delete by Default** - All business entities support restoration (Constitution 6.4)
- **Weighted Average Cost (WAC)** - Automatic WAC recalculation on stock-in (Constitution 6.5)
- **Atomic Safety** - `transaction.atomic` + `select_for_update()` for concurrency (Constitution 6.6)
- **Comprehensive Audit** - Before/after snapshots for all critical changes (Constitution 6.7)
- **Policy-Based IAM** - Reusable authorization: Employee → Department → Role → Policies
- **Immutable Stock Ledger** - All stock movements recorded with full traceability
- **Stock Adjustment Workflow** - Approval-based corrections with rejection comments

### Technology Stack

| Layer           | Technology                       |
|-----------------|----------------------------------|
| Backend         | Python 3.12, Django 4.2 LTS      |
| Database        | PostgreSQL 15                    |
| Cache/Broker    | Redis 7                          |
| Frontend        | HTMX, Django Templates, CSS      |
| Async           | Celery 5                         |
| Testing         | pytest, pytest-django            |
| Code Quality    | ruff, black, isort               |
| Deployment      | Docker, Gunicorn, WhiteNoise     |

---

## 📖 Documentation

- **[Constitution](Constitution_AMW_DJ_ERP.md)** - Project law and governing principles
- **[Phase 1 Foundation](Architecture/Phase_1_Foundation.md)** - Official Phase 1 plan and completion record
- **[Architecture Plans](Architecture/)** - Phase-by-phase execution plans
- **[Utility Scripts](utils/README.md)** - Script documentation

---

## 🔐 Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=amw_django_erp
DB_USER=amw_erp_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5433

# Redis
REDIS_URL=redis://localhost:6380/0
```

---

## 🧪 Testing

```bash
# Run all tests
./utils/test_suite_runner.sh

# Run specific test file
pytest core/tests/test_models.py -v

# Run with coverage
./utils/test_suite_runner.sh coverage
```

---

## 🤝 Team Roles

| Role              | Responsibility                                       |
|-------------------|------------------------------------------------------|
| **Manager**       | Ahmad - Final owner of scope and business decisions  |
| **Consultant AI** | Gem - Architecture auditor and strategic consistency |
| **Backend Lead**  | Qwen - Business logic, data integrity, IAM           |
| **Frontend Lead** | Cod - HTMX interactions, template architecture       |

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🎯 Next Steps

**Phase 8: Async Tasks, Reporting & Hardening**

- [ ] Celery and Redis integration
- [ ] Background report generation
- [ ] Query optimization audit (select_related, prefetch_related)
- [ ] Production settings lockdown
- [ ] Value-Based Authorization (Gem's note)
- [ ] Merge Phase 7 to master

---

*Last Updated: 2026-04-03*
*Phase 7 Status: ✅ COMPLETE (186 tests passing, ready for merge)*
*Phase 8 Status: ⏳ NEXT*
