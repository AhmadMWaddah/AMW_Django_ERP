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

| Phase       | Name                                         | Status           | Branch          |
|-------------|----------------------------------------------|------------------|-----------------|
| **Phase 1** | Foundation, Automation & Local Scaffolding   | ✅ **COMPLETE**  | `master`        |
| **Phase 2** | Infrastructure & Core Identity               | ✅ **COMPLETE**  | `phase-2`       |
| Phase 3     | IAM & Security Framework                     | ⏳ **NEXT**      | `phase-3`       |
| Phase 4     | Inventory Architecture & Valuation           | ⏳ Planned       | `phase-4`       |
| Phase 5     | Sales & CRM Workflows                        | ⏳ Planned       | `phase-5`       |
| Phase 6     | Purchasing & Procurement                     | ⏳ Planned       | `phase-6`       |
| Phase 7     | Frontend Foundation & HTMX UI                | ⏳ Planned       | `phase-7`       |
| Phase 8     | Async Tasks, Reporting & Hardening           | ⏳ Planned       | `phase-8`       |

**Branch Strategy:**
- `master` - Stable production baseline (Phase 1 complete)
- `phase-2` - Current development (Phase 2 complete, bug fixes in progress)
- Future phases will be developed in `phase-X` branches and merged to `master` after approval

**See `Architecture/Phase_2_Infrastructure_Identity.md` for Phase 2 completion details.**

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
./utils/env_factory.sh setup

# Activate environment
source .env_amw_dj_erp/bin/activate
```

### 2. Start Infrastructure (Docker)

```bash
# Start PostgreSQL and Redis
./utils/infra_manage.sh start

# Check services status
./utils/infra_manage.sh status
```

### 3. Initialize Database

```bash
# Run migrations
./utils/db_manage_dev.sh migrate

# Create admin superuser
./utils/db_manage_dev.sh createsuperuser
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
│   ├── git_task_commit.sh
│   ├── env_factory.sh
│   ├── test_suite_runner.sh
│   ├── db_manage_dev.sh
│   └── infra_manage.sh
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

```bash
# Git commits (atomic, task-based)
git add path/to/file
./utils/git_task_commit.sh "Your task description"

# Environment management
./utils/env_factory.sh setup
./utils/env_factory.sh init-git

# Testing
./utils/test_suite_runner.sh          # Run all tests
./utils/test_suite_runner.sh unit     # Unit tests only
./utils/test_suite_runner.sh coverage # With coverage
./utils/test_suite_runner.sh lint     # Run linters

# Database operations
./utils/db_manage_dev.sh migrate
./utils/db_manage_dev.sh shell
./utils/db_manage_dev.sh createsuperuser

# Infrastructure (Docker)
./utils/infra_manage.sh start
./utils/infra_manage.sh logs
./utils/infra_manage.sh status
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
- **Weighted Average Cost** - Automatic WAC recalculation on stock movements (Constitution 6.5)
- **Atomic Safety** - `transaction.atomic` + `select_for_update()` for concurrency (Constitution 6.6)
- **Comprehensive Audit** - Before/after snapshots for all critical changes (Constitution 6.7)
- **Policy-Based IAM** - Reusable authorization: Employee → Department → Role → Policies

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

**Phase 3: IAM & Security Framework**

- [ ] Department, Role, and Policy models
- [ ] Policy enforcement engine
- [ ] Audit logging system
- [ ] Integration with Employee model

---

*Last Updated: 2026-03-28*  
*Phase 1 Status: ✅ COMPLETE*
