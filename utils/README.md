# -- AMW Django ERP - Utility Scripts --

This directory contains official project utility scripts as defined in the Constitution (Section 8.2).

## Available Scripts

### 1. git_task_commit.sh
Atomic task-based commit script with **Multi-Message Format** (Constitution Section 9.3).

**Usage:**
```bash
git add path/to/file
./utils/git_task_commit.sh "Title" "Description"
```

**Examples:**
```bash
# Phase work
./utils/git_task_commit.sh "phase-2: Employee Model" "Added AbstractBaseUser with email auth"

# Bug fix
./utils/git_task_commit.sh "Fix: Navigation bug" "Changed to namespaced URLs accounts:dashboard"

# Feature
./utils/git_task_commit.sh "Feature: Open redirect protection" "Added Django's url_has_allowed_host_and_scheme"

# Documentation
./utils/git_task_commit.sh "Docs: Update README" "Added installation instructions for Docker"
```

**Title Prefixes:**
- `phase-X:` - Phase-related features (phase-1:, phase-2:, etc.)
- `Fix:` - Bug fixes
- `Feature:` - New features
- `Refactor:` - Code refactoring
- `Docs:` - Documentation updates
- `Test:` - Test additions or modifications

**Rules:**
- Both Title and Description are **mandatory**
- Title should be concise (under 72 characters)
- Description explains WHAT and WHY (not HOW)
- Commits staged changes only
- Requires an initialized Git repository
- **Local Quality Gate:** Runs mandatory lint check before committing

### 2. git_phase_finish.sh
Phase completion and merge automation script (Constitution Section 9.5).

**Usage:**
```bash
./utils/git_phase_finish.sh <phase-number> [version-tag]
```

**Examples:**
```bash
./utils/git_phase_finish.sh 3           # Finish phase 3 with auto tag
./utils/git_phase_finish.sh 3 v3.0     # Finish phase 3 with custom tag
```

**What it does:**
1. ✅ Runs full test suite (must pass)
2. ✅ Runs lint checks (must pass)
3. ✅ Merges phase branch to master
4. ✅ Creates version tag
5. ✅ Pushes master and tags to GitHub
6. ✅ Optionally cleans up phase branch

**Benefits:**
- Reduces 10 minutes of manual Git work to 5 seconds
- Eliminates human error in merge process
- Ensures consistent tagging across phases
- Automatic quality gates (tests + lint must pass)

### 3. env_factory.sh
Virtual environment management.
```bash
./utils/env_factory.sh setup     # Bootstrap git + venv + dependencies
./utils/env_factory.sh init-git  # Initialize git repository if missing
./utils/env_factory.sh create    # Create virtual environment
./utils/env_factory.sh install   # Install dependencies
./utils/env_factory.sh activate  # Check activation
./utils/env_factory.sh clean     # Remove environment
```

### 4. test_suite_runner.sh
Unified testing interface.
```bash
./utils/test_suite_runner.sh          # Run all tests
./utils/test_suite_runner.sh unit     # Unit tests only
./utils/test_suite_runner.sh coverage # With coverage report
./utils/test_suite_runner.sh lint     # Run linters
```

### 5. db_manage_dev.sh
Database operations for development.
```bash
./utils/db_manage_dev.sh migrate        # Run migrations
./utils/db_manage_dev.sh makemigrations # Create migrations
./utils/db_manage_dev.sh shell          # Django shell
./utils/db_manage_dev.sh createsuperuser
./utils/db_manage_dev.sh reset          # WARNING: Destructive
```

### 6. infra_manage.sh
Docker infrastructure management.
```bash
./utils/infra_manage.sh start    # Start services
./utils/infra_manage.sh stop     # Stop services
./utils/infra_manage.sh logs     # View logs
./utils/infra_manage.sh clean    # WARNING: Destructive
```

## Setup Instructions

1. Make scripts executable (if not already):
   ```bash
   chmod +x utils/*.sh
   ```

2. Bootstrap the project:
   ```bash
   ./utils/env_factory.sh setup
   ```

3. Activate environment:
   ```bash
   source .env_amw_dj_erp/bin/activate
   ```

## Script Standards

All scripts follow these conventions:
- Colored output for clarity
- Error handling with set -e
- Clear help messages
- Project-root aware (work from any directory)
