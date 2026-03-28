#!/bin/bash

# -- Git Task Commit Script --
# AMW Django ERP - Atomic Task-Based Committing
# 
# Usage: ./utils/git_task_commit.sh "Task description"
# Example: ./utils/git_task_commit.sh "Create env_factory.sh utility script"
#
# This script ensures atomic commits aligned with project tasks.

set -e

# -- Configuration --
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BRANCH_PREFIX="phase-1"

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
if [ $# -eq 0 ]; then
    print_error "No task description provided"
    echo "Usage: $0 \"Task description\""
    echo "Example: $0 \"Create env_factory.sh utility script\""
    exit 1
fi

TASK_DESCRIPTION="$1"

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
# Format: [Phase-X] Task description
COMMIT_MESSAGE="[$CURRENT_BRANCH] $TASK_DESCRIPTION"

# -- Confirm Commit --
print_header "Commit Preview"
echo "Branch: $CURRENT_BRANCH"
echo "Commit message: $COMMIT_MESSAGE"
echo ""
echo "Files to commit:"
git diff --cached --stat
echo ""

# -- Add All Changes and Commit --
print_header "Creating Commit"

git commit -m "$COMMIT_MESSAGE"

if [ $? -eq 0 ]; then
    print_success "Commit created successfully"
    echo ""
    echo "Commit details:"
    git log -1 --stat
else
    print_error "Commit failed"
    exit 1
fi

# -- Post-Commit Status --
print_header "Repository Status"
git status

print_success "Task commit completed for: $TASK_DESCRIPTION"
