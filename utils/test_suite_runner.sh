#!/bin/bash

# -- Test Suite Runner Script --
# AMW Django ERP - Unified Testing Interface
#
# Usage:
#   ./utils/test_suite_runner.sh              - Run all tests
#   ./utils/test_suite_runner.sh unit         - Run unit tests only
#   ./utils/test_suite_runner.sh integration  - Run integration tests only
#   ./utils/test_suite_runner.sh coverage     - Run tests with coverage report
#   ./utils/test_suite_runner.sh lint         - Run linting checks
#   ./utils/test_suite_runner.sh all          - Run tests + lint
#
# This script provides a unified interface for running tests.

set -e

# -- Configuration --
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.env_amw_dj_erp"
SETTINGS_MODULE="config.settings.dev"

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
    
    if [ ! -f "$VENV_PATH/bin/activate" ]; then
        print_error "Virtual environment activation script not found"
        exit 1
    fi
}

activate_venv() {
    source "$VENV_PATH/bin/activate"
    export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"
}

run_unit_tests() {
    print_header "Running Unit Tests"
    
    activate_venv
    
    # Run pytest for unit tests (excluding integration tests)
    python -m pytest \
        --tb=short \
        -v \
        -m "not integration" \
        "${@:-.}"
    
    if [ $? -eq 0 ]; then
        print_success "Unit tests passed"
    else
        print_error "Unit tests failed"
        return 1
    fi
}

run_integration_tests() {
    print_header "Running Integration Tests"
    
    activate_venv
    
    # Run pytest for integration tests only
    python -m pytest \
        --tb=short \
        -v \
        -m "integration" \
        "${@:-.}"
    
    if [ $? -eq 0 ]; then
        print_success "Integration tests passed"
    else
        print_error "Integration tests failed"
        return 1
    fi
}

run_all_tests() {
    print_header "Running All Tests"
    
    activate_venv
    
    python -m pytest \
        --tb=short \
        -v \
        "${@:-.}"
    
    if [ $? -eq 0 ]; then
        print_success "All tests passed"
    else
        print_error "Some tests failed"
        return 1
    fi
}

run_coverage() {
    print_header "Running Tests with Coverage"
    
    activate_venv
    
    python -m pytest \
        --tb=short \
        -v \
        --cov=. \
        --cov-report=html \
        --cov-report=term-missing \
        "${@:-.}"
    
    if [ $? -eq 0 ]; then
        print_success "Coverage report generated"
        print_info "Open htmlcov/index.html to view detailed report"
    else
        print_error "Tests with coverage failed"
        return 1
    fi
}

run_lint() {
    print_header "Running Linters"
    
    activate_venv
    
    LINT_FAILED=0
    
    # Run ruff (fast Python linter)
    print_info "Running ruff..."
    if python -m ruff --version &> /dev/null; then
        python -m ruff check . || LINT_FAILED=1
    else
        print_info "ruff not installed, skipping..."
    fi
    
    # Run black check (code formatting)
    print_info "Running black (check mode)..."
    if python -m black --version &> /dev/null; then
        python -m black --check . || LINT_FAILED=1
    else
        print_info "black not installed, skipping..."
    fi
    
    if [ $LINT_FAILED -eq 0 ]; then
        print_success "Linting passed"
    else
        print_error "Linting failed"
        return 1
    fi
}

run_format() {
    print_header "Formatting Code"
    
    activate_venv
    
    # Run black to format code
    print_info "Running black..."
    if python -m black --version &> /dev/null; then
        python -m black .
        print_success "Code formatted"
    else
        print_info "black not installed, skipping..."
    fi
}

run_all() {
    print_header "Running Complete Test Suite"
    
    run_lint || true
    run_all_tests
    run_coverage
}

show_usage() {
    print_header "Test Suite Runner"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  (none)      - Run all tests"
    echo "  unit        - Run unit tests only"
    echo "  integration - Run integration tests only"
    echo "  coverage    - Run tests with coverage report"
    echo "  lint        - Run linting checks"
    echo "  format      - Format code with black"
    echo "  all         - Run tests + lint + coverage"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 unit"
    echo "  $0 coverage"
    echo "  $0 lint"
}

# -- Main Script --
cd "$PROJECT_ROOT"

check_venv

case "${1:-}" in
    unit)
        shift
        run_unit_tests "$@"
        ;;
    integration)
        shift
        run_integration_tests "$@"
        ;;
    coverage)
        shift
        run_coverage "$@"
        ;;
    lint)
        run_lint
        ;;
    format)
        run_format
        ;;
    all)
        run_all
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        run_all_tests "$@"
        ;;
esac
