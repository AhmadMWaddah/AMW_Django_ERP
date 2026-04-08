#!/bin/bash

# -- Git Task Commit Script --
# AMW Django ERP - Atomic Task-Based Committing with Multi-Message Format
#
# Usage: bash utils/git_task_commit.sh "Title" "Description"
# Example: bash utils/git_task_commit.sh "Phase 2: Add auth views" "Implemented login, logout, and dashboard"
#
# This script ensures atomic commits with proper two-part messages for audit clarity.
# Constitution Section 6.3: Multi-Message Commit Format

set -e

# -- Configuration --
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

run_lint_check() {
    print_header "Running Lint Check (Quality Gate)"
    
    # Activate virtual environment if available
    if [ -d "$PROJECT_ROOT/.env_amw_dj_erp" ]; then
        source "$PROJECT_ROOT/.env_amw_dj_erp/bin/activate"
    fi
    
    cd "$PROJECT_ROOT"
    
    # Run ruff check
    print_info "Running ruff..."
    if python -m ruff check . --fix --ignore I001; then
        print_success "Ruff check passed"
    else
        print_error "Ruff check failed"
        print_info "Please fix linting errors before committing"
        print_info "Run: python -m ruff check . --fix"
        exit 1
    fi
    
    # Run black check
    print_info "Running black (check mode)..."
    if python -m black --check .; then
        print_success "Black check passed"
    else
        print_info "Formatting code with black..."
        python -m black .
        print_success "Code formatted"
        print_info "Please review formatted changes and re-commit"
    fi
    
    print_success "Lint check completed successfully"
}

# -- Validation --
if [ $# -lt 2 ]; then
    print_error "Both Title and Description are required"
    echo ""
    echo "Usage: bash utils/git_task_commit.sh \"Title\" \"Description\""
    echo ""
    echo "Examples:"
    echo "  bash utils/git_task_commit.sh \"Phase 2: Employee Model\" \"Added AbstractBaseUser with email auth\""
    echo "  bash utils/git_task_commit.sh \"Fix: Navigation bug\" \"Changed to namespaced URLs accounts:dashboard\""
    echo "  bash utils/git_task_commit.sh \"Feature: Open redirect protection\" \"Added Django's url_has_allowed_host_and_scheme\""
    echo ""
    echo "Title Prefixes:"
    echo "  Phase X:  - Phase-related features (Phase 2:, Phase 3:, etc.)"
    echo "  Fix:      - Bug fixes"
    echo "  Feature:  - New features"
    echo "  Refactor: - Code refactoring"
    echo "  Docs:     - Documentation updates"
    echo "  Test:     - Test additions or modifications"
    exit 1
fi

COMMIT_TITLE="$1"
COMMIT_DESCRIPTION="$2"

# -- Navigate to Project Root --
cd "$PROJECT_ROOT"

# -- Check Git Repository --
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    print_error "This directory is not a Git repository"
    print_info "Initialize Git first with: git init"
    exit 1
fi

# -- Check Git Status --
print_header "Git Status Check"

# Check if we're on a valid branch
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    print_error "Could not determine the current Git branch"
    exit 1
fi

print_info "Current branch: $CURRENT_BRANCH"

# Show staged changes only to preserve atomic task commits
STAGED_STATUS=$(git diff --cached --name-status)
if [ -z "$STAGED_STATUS" ]; then
    print_error "No staged changes to commit"
    print_info "Stage only the files for this task, then rerun this script"
    print_info "Example: git add path/to/file"
    exit 1
fi

echo "Changes to be committed:"
echo "$STAGED_STATUS"
echo ""

# -- Run Lint Check (Quality Gate) --
run_lint_check

# -- Create Commit Message --
# Format: Title + Description (Multi-Message)
# The title is used exactly as provided — no branch prefix added.
COMMIT_MESSAGE_TITLE="$COMMIT_TITLE"

# -- Confirm Commit --
print_header "Commit Preview"
echo "Branch: $CURRENT_BRANCH"
echo "Commit title: $COMMIT_MESSAGE_TITLE"
echo "Commit description: $COMMIT_DESCRIPTION"
echo ""
echo "Files to commit:"
git diff --cached --stat
echo ""

# -- Create Commit with Multi-Message Format --
print_header "Creating Commit"

git commit -m "$COMMIT_MESSAGE_TITLE" -m "$COMMIT_DESCRIPTION"

if [ $? -eq 0 ]; then
    print_success "Commit created successfully"
    echo ""
    echo "Commit details:"
    git log -1 --stat
    echo ""
    echo "Commit message preview:"
    git log -1 --format="%s%n%b" | head -10
else
    print_error "Commit failed"
    exit 1
fi

# -- Post-Commit Status --
print_header "Repository Status"
git status

print_success "Task commit completed: $COMMIT_TITLE"

# -- Auto-Push to Remote --
print_header "Pushing to Remote"

# Check if branch exists on remote
if git ls-remote --exit-code --heads origin "$CURRENT_BRANCH" > /dev/null 2>&1; then
    print_info "Branch '$CURRENT_BRANCH' exists on remote — pushing changes"
    git push origin "$CURRENT_BRANCH"
else
    print_info "Branch '$CURRENT_BRANCH' not found on remote — pushing with upstream tracking"
    git push -u origin "$CURRENT_BRANCH"
fi

if [ $? -eq 0 ]; then
    print_success "Pushed to origin/$CURRENT_BRANCH"
else
    print_error "Push to origin/$CURRENT_BRANCH failed"
    print_info "Local commit is intact. Push manually when ready:"
    print_info "  git push origin $CURRENT_BRANCH"
fi
