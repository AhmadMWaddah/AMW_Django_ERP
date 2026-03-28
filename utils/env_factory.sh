#!/bin/bash

# -- Environment Factory Script --
# AMW Django ERP - Virtual Environment Management
#
# Usage:
#   ./utils/env_factory.sh create    - Create/recreate virtual environment
#   ./utils/env_factory.sh init-git  - Initialize Git repository if missing
#   ./utils/env_factory.sh setup     - Initialize Git, create environment, install dependencies
#   ./utils/env_factory.sh activate  - Activate the virtual environment
#   ./utils/env_factory.sh install   - Install dependencies from requirements.txt
#   ./utils/env_factory.sh clean     - Remove virtual environment
#
# This script manages the .env_amw_dj_erp/ virtual environment and setup bootstrap.

set -e

# -- Configuration --
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_NAME=".env_amw_dj_erp"
VENV_PATH="$PROJECT_ROOT/$VENV_NAME"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
PYTHON_VERSION="python3"
GITHUB_REPO_NAME="AMW_Django_ERP"

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

check_python() {
    if ! command -v $PYTHON_VERSION &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.10 or higher."
        exit 1
    fi
    
    PYTHON_FULL_VERSION=$($PYTHON_VERSION --version 2>&1)
    print_info "Found: $PYTHON_FULL_VERSION"
}

check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
}

check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed."
        print_info "Install it from: https://cli.github.com/"
        print_info "Skipping GitHub repository creation."
        return 1
    fi
    return 0
}

check_gh_auth() {
    if ! check_gh_cli; then
        return 1
    fi
    
    print_info "Checking GitHub authentication status..."
    if gh auth status &> /dev/null; then
        print_success "GitHub authentication verified"
        return 0
    else
        print_error "Not authenticated with GitHub CLI"
        print_info "Run 'gh auth login' to authenticate"
        print_info "Skipping GitHub repository creation."
        return 1
    fi
}

create_github_repo() {
    print_header "GitHub Repository Creation"
    
    if ! check_gh_auth; then
        return 0
    fi
    
    # Check if remote already exists
    if git remote get-url origin &> /dev/null; then
        print_info "Remote 'origin' already configured"
        ORIGIN_URL=$(git remote get-url origin)
        print_info "Current remote: $ORIGIN_URL"
        read -p "Do you want to change it to a new GitHub repository? (y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing remote"
            return 0
        fi
    fi
    
    # Prompt for repository creation
    print_info "Repository name: $GITHUB_REPO_NAME"
    read -p "Do you want to create a remote repository on GitHub? (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping GitHub repository creation"
        return 0
    fi
    
    # Ask for visibility
    read -p "Create as private repository? (y/n): " -n 1 -r
    echo ""
    VISIBILITY="--private"
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        VISIBILITY="--public"
        print_info "Creating public repository"
    else
        print_info "Creating private repository"
    fi
    
    # Create the repository
    print_info "Creating GitHub repository: $GITHUB_REPO_NAME"
    
    # Try to create, handle existing repo gracefully
    if gh repo create "$GITHUB_REPO_NAME" $VISIBILITY --source=. --remote=origin --push 2>&1 | grep -q "already exists"; then
        print_info "Repository already exists on GitHub"
        print_info "Linking existing remote..."
        
        # Get the current user's GitHub username
        GH_USER=$(gh api user | jq -r .login 2>/dev/null || echo "")
        
        if [ -n "$GH_USER" ]; then
            REMOTE_URL="https://github.com/${GH_USER}/${GITHUB_REPO_NAME}.git"
            git remote remove origin 2>/dev/null || true
            git remote add origin "$REMOTE_URL"
            print_success "Linked to existing repository: $REMOTE_URL"
        else
            print_info "Could not determine GitHub username"
            print_info "Please manually set the remote URL"
            print_info "Example: git remote add origin https://github.com/YOUR_USERNAME/$GITHUB_REPO_NAME.git"
        fi
    else
        REPO_URL="https://github.com/$(gh api user | jq -r .login 2>/dev/null || echo 'YOUR_USERNAME')/$GITHUB_REPO_NAME"
        print_success "GitHub repository created successfully"
        print_info "Repository URL: $REPO_URL"
    fi
}

init_git_repo() {
    print_header "Git Repository Setup"

    check_git

    if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        print_info "Git repository already initialized"
        print_info "Repository root: $(git rev-parse --show-toplevel)"
        
        # Offer to create GitHub repo even if git is already initialized
        read -p "Do you want to configure GitHub remote? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_github_repo
        fi
        return 0
    fi

    print_info "Initializing Git repository at: $PROJECT_ROOT"
    git init
    print_success "Git repository initialized successfully"
    
    # Offer to create GitHub repository
    create_github_repo
}

create_venv() {
    print_header "Creating Virtual Environment"
    
    if [ -d "$VENV_PATH" ]; then
        print_info "Virtual environment already exists at: $VENV_PATH"
        read -p "Do you want to recreate it? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf "$VENV_PATH"
        else
            print_info "Keeping existing virtual environment"
            return 0
        fi
    fi
    
    print_info "Creating virtual environment at: $VENV_PATH"
    $PYTHON_VERSION -m venv "$VENV_PATH"
    
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created successfully"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
}

activate_venv() {
    # Note: This function is mainly for internal use
    # In practice, users should source the activate script directly
    if [ -f "$VENV_PATH/bin/activate" ]; then
        print_success "Virtual environment exists and can be activated"
        print_info "To activate, run: source $VENV_NAME/bin/activate"
    else
        print_error "Virtual environment not found. Run 'create' first."
        exit 1
    fi
}

install_deps() {
    print_header "Installing Dependencies"
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "requirements.txt not found at: $REQUIREMENTS_FILE"
        print_info "Please create requirements.txt first"
        exit 1
    fi
    
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found. Run 'create' first."
        exit 1
    fi
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    print_info "Installing dependencies from requirements.txt..."
    pip install -r "$REQUIREMENTS_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
        print_info "Installed packages:"
        pip list
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
    
    # Deactivate
    deactivate
}

clean_venv() {
    print_header "Cleaning Virtual Environment"
    
    if [ -d "$VENV_PATH" ]; then
        read -p "Are you sure you want to remove the virtual environment? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing virtual environment..."
            rm -rf "$VENV_PATH"
            print_success "Virtual environment removed"
        else
            print_info "Cancelled"
        fi
    else
        print_info "Virtual environment does not exist"
    fi
}

setup_project() {
    print_header "Project Setup Bootstrap"
    init_git_repo
    check_python
    create_venv
    install_deps
    print_success "Project setup completed"
    print_info "Next steps:"
    print_info "1. source $VENV_NAME/bin/activate"
    print_info "2. Review .env values"
    print_info "3. Start infrastructure with ./utils/infra_manage.sh start"
}

show_usage() {
    print_header "Environment Factory"
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  create    - Create/recreate the virtual environment"
    echo "  init-git  - Initialize Git repository (with optional GitHub remote)"
    echo "  setup     - Bootstrap Git, environment, and dependencies"
    echo "  activate  - Check if environment can be activated"
    echo "  install   - Install dependencies from requirements.txt"
    echo "  clean     - Remove the virtual environment"
    echo "  help      - Show this help message"
    echo ""
    echo "GitHub Integration:"
    echo "  - Requires GitHub CLI (gh) installed and authenticated"
    echo "  - Run 'gh auth login' to authenticate before using GitHub features"
    echo "  - The init-git command will prompt to create a GitHub repository"
    echo ""
    echo "Examples:"
    echo "  $0 create"
    echo "  $0 init-git           # Will prompt for GitHub repo creation"
    echo "  $0 setup              # Full bootstrap with GitHub option"
    echo "  $0 install"
    echo "  source $VENV_NAME/bin/activate  # Then activate manually"
}

# -- Main Script --
cd "$PROJECT_ROOT"

case "${1:-}" in
    create)
        check_python
        create_venv
        ;;
    init-git)
        init_git_repo
        ;;
    setup)
        setup_project
        ;;
    activate)
        activate_venv
        ;;
    install)
        install_deps
        ;;
    clean)
        clean_venv
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Invalid or missing command"
        show_usage
        exit 1
        ;;
esac
