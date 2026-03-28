#!/bin/bash

# -- Database Management Script (Development) --
# AMW Django ERP - Database Operations for Development
#
# Usage:
#   ./utils/db_manage_dev.sh migrate     - Run migrations
#   ./utils/db_manage_dev.sh makemigrations - Create new migrations
#   ./utils/db_manage_dev.sh reset       - Reset database (WARNING: destructive)
#   ./utils/db_manage_dev.sh shell       - Open Django shell
#   ./utils/db_manage_dev.sh createsuperuser - Create admin user
#   ./utils/db_manage_dev.sh status      - Show database status
#
# This script manages development database operations.

set -e

# -- Configuration --
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.env_amw_dj_erp"
SETTINGS_MODULE="config.settings.dev"
MANAGE_PY="$PROJECT_ROOT/manage.py"

# -- Colors for Output --
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# -- Helper Functions --
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

print_info() {
    echo -e "${YELLOW}INFO: $1${NC}"
}

check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found at: $VENV_PATH"
        print_info "Run './utils/env_factory.sh create' first"
        exit 1
    fi
}

activate_venv() {
    source "$VENV_PATH/bin/activate"
}

check_manage_py() {
    if [ ! -f "$MANAGE_PY" ]; then
        print_error "manage.py not found at: $MANAGE_PY"
        print_info "Make sure Django project is initialized"
        exit 1
    fi
}

run_migrations() {
    print_header "Running Database Migrations"
    
    activate_venv
    check_manage_py
    
    python "$MANAGE_PY" migrate --settings=$SETTINGS_MODULE
    
    if [ $? -eq 0 ]; then
        print_success "Migrations completed successfully"
    else
        print_error "Migrations failed"
        return 1
    fi
}

make_migrations() {
    print_header "Creating Database Migrations"
    
    activate_venv
    check_manage_py
    
    APP_NAME="${1:-}"
    
    if [ -n "$APP_NAME" ]; then
        print_info "Creating migrations for app: $APP_NAME"
        python "$MANAGE_PY" makemigrations "$APP_NAME" --settings=$SETTINGS_MODULE
    else
        print_info "Creating migrations for all apps"
        python "$MANAGE_PY" makemigrations --settings=$SETTINGS_MODULE
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Migrations created successfully"
    else
        print_error "Failed to create migrations"
        return 1
    fi
}

reset_database() {
    print_header "Database Reset (WARNING: Destructive)"
    
    print_error "This will DELETE ALL DATA in the database!"
    read -p "Are you sure you want to continue? Type 'yes' to confirm: " -r
    echo ""
    
    if [[ $REPLY != "yes" ]]; then
        print_info "Cancelled by user"
        return 0
    fi
    
    activate_venv
    check_manage_py
    
    # Flush database (remove all data, keep schema)
    print_info "Flushing database..."
    python "$MANAGE_PY" flush --settings=$SETTINGS_MODULE --noinput
    
    # Delete migration files (optional, commented out for safety)
    # print_info "Deleting migration files..."
    # find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    
    print_success "Database reset completed"
    print_info "You may need to run migrations again"
}

open_shell() {
    print_header "Opening Django Shell"
    
    activate_venv
    check_manage_py
    
    python "$MANAGE_PY" shell --settings=$SETTINGS_MODULE
}

create_superuser() {
    print_header "Create Superuser"
    
    activate_venv
    check_manage_py
    
    python "$MANAGE_PY" createsuperuser --settings=$SETTINGS_MODULE
}

show_status() {
    print_header "Database Status"
    
    activate_venv
    check_manage_py
    
    print_info "Checking migrations..."
    python "$MANAGE_PY" showmigrations --settings=$SETTINGS_MODULE
    
    echo ""
    print_info "Database configuration:"
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$SETTINGS_MODULE')
django.setup()
from django.conf import settings
db = settings.DATABASES['default']
print(f\"Engine: {db['ENGINE']}\")
print(f\"Name: {db['NAME']}\")
print(f\"Host: {db.get('HOST', 'localhost')}\")
print(f\"Port: {db.get('PORT', '5432')}\")
" 2>/dev/null || print_info "Could not retrieve database info (Django may not be fully configured yet)"
}

show_help() {
    print_header "Database Management (Development)"
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  migrate         - Run database migrations"
    echo "  makemigrations  - Create new migrations"
    echo "  makemigrations <app> - Create migrations for specific app"
    echo "  reset           - Reset database (WARNING: destructive)"
    echo "  shell           - Open Django shell"
    echo "  createsuperuser - Create admin superuser"
    echo "  status          - Show database and migrations status"
    echo "  help            - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 migrate"
    echo "  $0 makemigrations inventory"
    echo "  $0 createsuperuser"
}

# -- Main Script --
cd "$PROJECT_ROOT"

check_venv

case "${1:-}" in
    migrate)
        run_migrations
        ;;
    makemigrations)
        shift
        make_migrations "$@"
        ;;
    reset)
        reset_database
        ;;
    shell)
        open_shell
        ;;
    createsuperuser)
        create_superuser
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Invalid or missing command"
        show_help
        exit 1
        ;;
esac
