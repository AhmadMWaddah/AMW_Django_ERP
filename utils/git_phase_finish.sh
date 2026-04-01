#!/bin/bash

# -- Git Phase Finish Script --
# AMW Django ERP - Phase Completion and Merge Automation
#
# Usage: ./utils/git_phase_finish.sh <phase-number> [version-tag] [--force]
# Example: ./utils/git_phase_finish.sh 3 v3.0
# Example: ./utils/git_phase_finish.sh 3 3.0-phase3-complete
# Example: ./utils/git_phase_finish.sh 3 --force  # Skip confirmation
#
# This script automates the complete phase closure process:
# 1. Runs full test suite
# 2. Runs lint checks
# 3. Merges phase branch to master
# 4. Creates version tag
# 5. Pushes everything to GitHub
#
# Constitution Section 9.4: Merge Rule

set -e

# -- Configuration --
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# -- Parse Arguments --
FORCE="false"
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE="true"
            shift
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

set -- "${POSITIONAL_ARGS[@]}"

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

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# -- Validation --
if [ $# -lt 1 ]; then
    print_error "Phase number is required"
    echo ""
    echo "Usage: $0 <phase-number> [version-tag]"
    echo ""
    echo "Examples:"
    echo "  $0 3                    # Finish phase 3 with auto-generated tag"
    echo "  $0 3 v3.0              # Finish phase 3 with tag v3.0"
    echo "  $0 3 3.0-phase3        # Finish phase 3 with custom tag"
    exit 1
fi

PHASE_NUMBER="$1"
VERSION_TAG="${2:-v${PHASE_NUMBER}.0-phase${PHASE_NUMBER}-complete}"
PHASE_BRANCH="phase-${PHASE_NUMBER}"

# -- Navigate to Project Root --
cd "$PROJECT_ROOT"

# -- Check Git Repository --
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    print_error "This directory is not a Git repository"
    exit 1
fi

# -- Check Current Branch --
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$PHASE_BRANCH" ]; then
    print_error "You must be on $PHASE_BRANCH branch to finish this phase"
    print_info "Current branch: $CURRENT_BRANCH"
    print_info "Run: git checkout $PHASE_BRANCH"
    exit 1
fi

# -- Step 1: Run Full Test Suite --
print_header "Step 1: Running Full Test Suite"

if [ -d "$PROJECT_ROOT/.env_amw_dj_erp" ]; then
    source "$PROJECT_ROOT/.env_amw_dj_erp/bin/activate"
fi

cd "$PROJECT_ROOT"

if ./utils/test_suite_runner.sh; then
    print_success "All tests passed"
else
    print_error "Test suite failed"
    print_warning "Please fix failing tests before finishing the phase"
    exit 1
fi

# -- Step 2: Run Lint Checks --
print_header "Step 2: Running Lint Checks"

if python -m ruff check . --fix --ignore I001; then
    print_success "Ruff check passed"
else
    print_error "Ruff check failed"
    print_warning "Please fix linting errors before finishing the phase"
    exit 1
fi

if python -m black --check .; then
    print_success "Black check passed"
else
    print_info "Formatting code with black..."
    python -m black .
    print_success "Code formatted. Please commit formatting changes first."
    exit 0
fi

print_success "All lint checks passed"

# -- Step 3: Confirm Phase Completion --
print_header "Step 3: Phase Completion Confirmation"

echo ""
echo "Phase ${PHASE_NUMBER} Completion Summary:"
echo "  Branch: $PHASE_BRANCH"
echo "  Version Tag: $VERSION_TAG"
echo "  Target: master branch"
echo ""
print_warning "This will:"
echo "  1. Merge $PHASE_BRANCH into master"
echo "  2. Create tag $VERSION_TAG"
echo "  3. Push master and tags to GitHub"
echo ""

# Auto-confirm if input is piped (non-interactive) or if --force flag is used
if [ -t 0 ] && [ "$FORCE" != "true" ]; then
    # Interactive mode
    read -p "Are you sure you want to finish Phase ${PHASE_NUMBER}? (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Phase completion cancelled"
        exit 0
    fi
else
    # Non-interactive mode (piped input or --force)
    print_info "Non-interactive mode: auto-confirming"
fi

# -- Step 4: Merge to Master --
print_header "Step 4: Merging to Master"

git checkout master

if git merge "$PHASE_BRANCH" -m "Merge $PHASE_BRANCH: Phase ${PHASE_NUMBER} Complete"; then
    print_success "Successfully merged $PHASE_BRANCH into master"
else
    print_error "Merge failed"
    print_warning "Please resolve merge conflicts manually"
    exit 1
fi

# -- Step 5: Create Version Tag --
print_header "Step 5: Creating Version Tag"

TAG_MESSAGE="Phase ${PHASE_NUMBER} Complete - AMW Django ERP v${PHASE_NUMBER}.0"

if git tag -a "$VERSION_TAG" -m "$TAG_MESSAGE"; then
    print_success "Created tag: $VERSION_TAG"
else
    print_error "Failed to create tag"
    print_warning "Tag may already exist. Use a different version tag."
    exit 1
fi

# -- Step 6: Push to GitHub --
print_header "Step 6: Pushing to GitHub"

print_info "Pushing master branch..."
if git push origin master; then
    print_success "Pushed master to GitHub"
else
    print_error "Failed to push master"
    print_warning "Please push manually: git push origin master"
    exit 1
fi

print_info "Pushing tags..."
if git push origin "$VERSION_TAG"; then
    print_success "Pushed tag $VERSION_TAG to GitHub"
else
    print_error "Failed to push tag"
    print_warning "You can push tags manually: git push origin $VERSION_TAG"
fi

# -- Step 7: Cleanup (Automatic Branch Removal) --
print_header "Step 7: Cleanup"

# Automatically delete local phase branch
print_info "Deleting local branch: $PHASE_BRANCH"
if git branch -d "$PHASE_BRANCH" 2>/dev/null; then
    print_success "Deleted local branch: $PHASE_BRANCH"
else
    print_info "Local branch may already be deleted"
fi

# Automatically delete remote phase branch
print_info "Deleting remote branch: origin/$PHASE_BRANCH"
if git push origin --delete "$PHASE_BRANCH" 2>/dev/null; then
    print_success "Deleted remote branch: $PHASE_BRANCH"
else
    print_info "Remote branch may not exist or already deleted"
fi

# Ask about keeping backup branch (optional)
echo ""
read -p "Create a backup branch before deletion? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    BACKUP_BRANCH="backup/${PHASE_BRANCH}-$(date +%Y%m%d)"
    git checkout "$VERSION_TAG" -b "$BACKUP_BRANCH"
    git push origin "$BACKUP_BRANCH"
    print_success "Created backup branch: $BACKUP_BRANCH"
    git checkout master
fi

# -- Completion Summary --
print_header "Phase ${PHASE_NUMBER} Complete! 🎉"

echo ""
echo "Summary:"
echo "  ✅ All tests passed"
echo "  ✅ All lint checks passed"
echo "  ✅ Merged to master"
echo "  ✅ Created tag: $VERSION_TAG"
echo "  ✅ Pushed to GitHub"
echo ""
echo "Next Steps:"
echo "  1. Verify deployment on staging/production"
echo "  2. Create phase-${PHASE_NUMBER} branch for next phase"
echo "  3. Begin Phase $((PHASE_NUMBER + 1)) development"
echo ""
print_success "Phase ${PHASE_NUMBER} successfully completed!"
