#!/bin/bash

# -- Git Task Commit Script --
# AMW Django ERP - Atomic Task-Based Committing with Multi-Message Format
#
# Usage: ./utils/git_task_commit.sh "Title" "Description"
# Example: ./utils/git_task_commit.sh "phase-2: Add auth views" "Implemented login, logout, and dashboard"
#
# This script ensures atomic commits with proper two-part messages for audit clarity.
# Constitution Section 9.3: Multi-Message Commit Format

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

# -- Validation --
if [ $# -lt 2 ]; then
    print_error "Both Title and Description are required"
    echo ""
    echo "Usage: $0 \"Title\" \"Description\""
    echo ""
    echo "Examples:"
    echo "  $0 \"phase-2: Employee Model\" \"Added AbstractBaseUser with email auth\""
    echo "  $0 \"Fix: Navigation bug\" \"Changed to namespaced URLs accounts:dashboard\""
    echo "  $0 \"Feature: Open redirect protection\" \"Added Django's url_has_allowed_host_and_scheme\""
    echo ""
    echo "Title Prefixes:"
    echo "  phase-X:  - Phase-related features (phase-1:, phase-2:, etc.)"
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

# -- Create Commit Message --
# Format: [branch] Title + Description (Multi-Message)
COMMIT_MESSAGE_TITLE="[$CURRENT_BRANCH] $COMMIT_TITLE"

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
