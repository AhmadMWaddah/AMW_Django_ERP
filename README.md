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
| **Phase 7** | Frontend Foundation & HTMX UI                | ✅ **COMPLETE**  | `master`  |
| **Phase 7.5**| Infrastructure UI & Global Pagination       | ✅ **COMPLETE**  | `master`  |
| Phase 8     | Async Tasks, Reporting & Hardening           | ⏳ NEXT          | `Phase 8: Async_Hardening` |

**Branch Strategy:**
- `master` - Stable production baseline (Phases 1-7.5 complete)
- All branches merged and cleaned up after completion
- Branch naming follows Constitution Section 6.2: `Fix: {Name}`, `Feature: {Name}`, `Phase {X}: {Name}`

**Version Tags:**
- `v3.0-phase3-complete` - IAM & Security Framework
- `v4.0-phase4-complete` - Inventory Architecture & Valuation
- `v5.0-phase5-complete` - Sales & CRM Workflows
- `v6.0-phase6-complete` - Purchasing & Procurement
- `v7.0-phase7-complete` - Frontend Foundation & HTMX UI
- `v7.5.0-phase7.5-complete` - Infrastructure UI & Global Pagination

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

# Seed dummy data (optional, for development)
python manage.py seed_erp
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

**Default Credentials:**
- **Owner (Superuser):** `amw@amw.io` / `12`
- **Warehouse Lead:** `warehouse.lead@amw.io` / `password123`
- **Sales Manager:** `sales.manager@amw.io` / `password123`
- **Auditor:** `auditor@amw.io` / `password123`

---

## 📁 Project Structure

```
AMW_Django_ERP/
│
├── Architecture/              # Phase execution plans
│   ├── Phase_1_Foundation.md
│   ├── Phase_2_Infrastructure_Identity.md
│   ├── Phase_3_IAM_Security.md
│   ├── Phase_4_Inventory_Valuation.md
│   ├── Phase_5_Sales_CRM.md
│   ├── Phase_6_Purchasing_Procurement.md
│   ├── Phase_7_Frontend_HTMX.md
│   ├── Phase_7.5_Infrastructure_UI_Pagination.md
│   └── Phase_8_Async_Hardening.md
│
├── Brand/                     # Brand assets and color palette
│   └── Dj_ERP_Colour_Pallete_CSS.scss
│
├── config/                    # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py           # Shared settings
│       ├── dev.py            # Development settings
│       └── prod.py           # Production settings
│
├── core/                      # Core app (base models, utilities)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py # Global UI context (nav, app state)
│   ├── models.py             # SoftDeleteModel base class
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── utils/                     # Utility scripts
│   ├── README.md
│   ├── db_manage_dev.sh      # Database operations
│   ├── env_factory.sh        # Environment bootstrap
│   ├── git_phase_finish.sh   # Phase merge & tagging
│   ├── git_task_commit.sh    # Atomic commits with lint
│   ├── infra_manage.sh       # Docker infrastructure
│   └── test_suite_runner.sh  # Testing & Linting
│
├── templates/                 # Global templates (centralized)
│   ├── _snipps_/             # Atomic UI fragments
│   │   ├── _button_.html
│   │   ├── _field_error_.html
│   │   ├── _icon_.html       # Lucide SVG icons
│   │   ├── _input_.html
│   │   └── _pagination_.html
│   ├── components/           # Global shared components
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   ├── topbar.html
│   │   └── table_frame.html
│   ├── accounts/             # Authentication pages
│   ├── admin/                # Custom admin overrides
│   ├── audit/                # Audit log list/detail pages
│   ├── core/errors/          # 404.html, 500.html
│   ├── inventory/            # Module-specific pages
│   ├── layouts/
│   │   ├── base.html         # Root layout shell
│   │   └── dashboard.html    # Dashboard layout
│   ├── purchasing/           # Module-specific pages
│   ├── sales/                # Module-specific pages
│   ├── security/             # IAM detail pages
│   └── health.html
│
├── static/                    # Static files (centralized)
│   ├── images/
│   │   ├── AMW_DJ_ERP_Logo.png
│   │   └── AMW_DJ_ERP_Fav_Icon.png
│   ├── scripts/
│   │   ├── htmx.min.js       # HTMX 1.9.12 (local)
│   │   └── toast_modal.min.js
│   └── styles/
│       ├── _variables.css    # Brand tokens, spacing, typography
│       ├── _base.css         # CSS resets
│       ├── _layout.css       # Sidebar, topbar, cards, tables, modals
│       ├── _utilities.css    # Micro-spacing, flexbox, text utils
│       ├── accounts.css      # Auth page styles
│       └── errors.css        # Error page styles
│
├── media/                     # User-uploaded media (gitignored)
│
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI/CD pipeline
│
├── accounts/                  # Employee identity & auth
│   ├── models.py             # Employee (AbstractBaseUser)
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── security/                  # IAM & Policy enforcement
│   ├── models.py             # Department, Role, Policy
│   ├── logic/
│   │   └── enforcement.py    # PolicyEngine
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── audit/                     # Audit logging
│   ├── models.py             # AuditLog
│   ├── logic/
│   │   └── logging.py
│   └── tests.py
│
├── inventory/                 # Product catalog & stock
│   ├── models.py             # Category, Product, StockTransaction, StockAdjustment
│   ├── operations/
│   │   └── stock.py          # stock_in, stock_out, approve_adjustment
│   ├── admin.py              # Full admin with StockAdjustment workflow
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── sales/                     # CRM & order workflows
│   ├── models.py             # Customer, SalesOrder, SalesOrderItem
│   ├── operations/
│   │   └── orders.py         # create_order, confirm_order, void_order, update_payment
│   ├── logic/
│   │   └── pricing.py        # Decimal pricing with ROUND_HALF_UP
│   ├── views.py              # Server-side PolicyEnforce authorization
│   ├── urls.py
│   └── tests.py
│
├── purchasing/                # Supplier & procurement
│   ├── models.py             # Supplier, PurchaseOrder, PurchaseOrderItem
│   ├── operations/
│   │   └── orders.py         # generate_po_number, issue_order, receive_items, cancel_order
│   ├── views.py              # Server-side PolicyEnforce authorization
│   ├── urls.py
│   └── tests.py
│
├── conftest.py               # pytest fixtures
├── manage.py                 # Django CLI
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Tool configuration (ruff, black, pytest)
├── docker-compose.yml       # PostgreSQL + Redis services
├── Dockerfile               # Application container
├── .env.example             # Environment template
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

**Database Operations:**
```bash
bash utils/db_manage_dev.sh migrate      # Apply migrations
bash utils/db_manage_dev.sh shell        # Django shell
bash utils/db_manage_dev.sh createsuperuser  # Create admin user
bash utils/db_manage_dev.sh reset        # Reset database (WARNING: destructive)
```

**Infrastructure (Docker):**
```bash
bash utils/infra_manage.sh start         # Start PostgreSQL + Redis
bash utils/infra_manage.sh logs          # View container logs
bash utils/infra_manage.sh status        # Check service status
bash utils/infra_manage.sh stop          # Stop services
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
- **Server-Side Authorization** - PolicyEngine enforced on all state-changing POST endpoints (403 + HTMX toast on denial)
- **Soft Delete by Default** - All business entities support restoration (Constitution 8.4)
- **Weighted Average Cost (WAC)** - Automatic WAC recalculation on stock-in (Constitution 8.5)
- **Atomic Safety** - `transaction.atomic` + `select_for_update()` for concurrency (Constitution 8.6)
- **Comprehensive Audit** - Before/after snapshots for all critical changes (Constitution 8.7)
- **Policy-Based IAM** - Reusable authorization: Employee → Department → Role → Policies
- **Immutable Stock Ledger** - All stock movements recorded with full traceability
- **Stock Adjustment Workflow** - Approval-based corrections with rejection comments
- **Atomic Order Numbering** - Unique sequential IDs (#Eg-00001) generated in operations layer
- **Enterprise Slug System** - URL-friendly slugs on all models for clean routing
- **HTMX-First Frontend** - Dynamic UI without heavy JavaScript frameworks

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
| CI/CD           | GitHub Actions                   |

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
bash utils/test_suite_runner.sh

# Run specific test file
pytest core/tests/test_models.py -v

# Run with coverage
bash utils/test_suite_runner.sh coverage
```

---

## 🤝 Team Roles

| Role              | Responsibility                                       |
|-------------------|------------------------------------------------------|
| **Owner**         | Ahmad - Final owner of scope and business decisions  |
| **Developer**     | Implementation, business logic, data integrity      |
| **Reviewer**     | Code review, quality gates                          |

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
- [ ] Value-Based Authorization

---

*Last Updated: 2026-04-06*
*Phase 7.5 Status: ✅ COMPLETE (217 tests passing, merged to master)*
*Phase 8 Status: ⏳ NEXT*
