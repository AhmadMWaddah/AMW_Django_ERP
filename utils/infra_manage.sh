#!/bin/bash

# -- Infrastructure Management Script --
# AMW Django ERP - Docker Infrastructure Operations
#
# Usage:
#   ./utils/infra_manage.sh start      - Start all services (PostgreSQL, Redis, etc.)
#   ./utils/infra_manage.sh stop       - Stop all services
#   ./utils/infra_manage.sh restart    - Restart all services
#   ./utils/infra_manage.sh status     - Show service status
#   ./utils/infra_manage.sh logs       - Show service logs
#   ./utils/infra_manage.sh clean      - Remove containers and volumes (WARNING: destructive)
#   ./utils/infra_manage.sh build      - Build/rebuild Docker images
#
# This script manages Docker-based infrastructure services.

set -e

# -- Configuration --
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

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

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        print_info "Please install Docker and Docker Compose"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        # Check for newer docker compose plugin
        if ! docker compose version &> /dev/null; then
            print_error "Docker Compose is not installed"
            print_info "Please install Docker Compose"
            exit 1
        fi
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    print_info "Using compose command: $COMPOSE_CMD"
}

check_compose_file() {
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        print_error "docker-compose.yml not found at: $DOCKER_COMPOSE_FILE"
        print_info "Please create docker-compose.yml first"
        exit 1
    fi
}

docker_start() {
    print_header "Starting Infrastructure Services"
    
    check_docker
    check_compose_file
    
    cd "$PROJECT_ROOT"
    
    $COMPOSE_CMD up -d
    
    if [ $? -eq 0 ]; then
        print_success "Services started successfully"
        echo ""
        print_info "Running services:"
        $COMPOSE_CMD ps
    else
        print_error "Failed to start services"
        return 1
    fi
}

docker_stop() {
    print_header "Stopping Infrastructure Services"
    
    check_docker
    check_compose_file
    
    cd "$PROJECT_ROOT"
    
    $COMPOSE_CMD stop
    
    if [ $? -eq 0 ]; then
        print_success "Services stopped successfully"
    else
        print_error "Failed to stop services"
        return 1
    fi
}

docker_restart() {
    print_header "Restarting Infrastructure Services"
    
    check_docker
    check_compose_file
    
    cd "$PROJECT_ROOT"
    
    $COMPOSE_CMD restart
    
    if [ $? -eq 0 ]; then
        print_success "Services restarted successfully"
    else
        print_error "Failed to restart services"
        return 1
    fi
}

docker_status() {
    print_header "Infrastructure Services Status"
    
    check_docker
    check_compose_file
    
    cd "$PROJECT_ROOT"
    
    echo "Running containers:"
    $COMPOSE_CMD ps
    
    echo ""
    print_info "Service ports:"
    echo "  - PostgreSQL: localhost:5433"
    echo "  - Redis:      localhost:6380"
}

docker_logs() {
    print_header "Infrastructure Services Logs"
    
    check_docker
    check_compose_file
    
    cd "$PROJECT_ROOT"
    
    SERVICE="${1:-}"
    
    if [ -n "$SERVICE" ]; then
        print_info "Showing logs for: $SERVICE"
        $COMPOSE_CMD logs -f "$SERVICE"
    else
        print_info "Showing logs for all services (Ctrl+C to exit)"
        $COMPOSE_CMD logs -f
    fi
}

docker_clean() {
    print_header "Cleaning Infrastructure (WARNING: Destructive)"
    
    print_error "This will remove ALL containers and VOLUMES (data)!"
    read -p "Are you sure you want to continue? Type 'yes' to confirm: " -r
    echo ""
    
    if [[ $REPLY != "yes" ]]; then
        print_info "Cancelled by user"
        return 0
    fi
    
    check_docker
    check_compose_file
    
    cd "$PROJECT_ROOT"
    
    print_info "Stopping services..."
    $COMPOSE_CMD down -v
    
    if [ $? -eq 0 ]; then
        print_success "Infrastructure cleaned successfully"
        print_info "All containers and volumes removed"
    else
        print_error "Failed to clean infrastructure"
        return 1
    fi
}

docker_build() {
    print_header "Building Docker Images"
    
    check_docker
    check_compose_file
    
    cd "$PROJECT_ROOT"
    
    $COMPOSE_CMD build --no-cache
    
    if [ $? -eq 0 ]; then
        print_success "Images built successfully"
    else
        print_error "Failed to build images"
        return 1
    fi
}

docker_shell() {
    print_header "Opening Shell in Service"
    
    check_docker
    check_compose_file
    
    cd "$PROJECT_ROOT"
    
    SERVICE="${1:-web}"
    
    print_info "Opening shell in: $SERVICE"
    $COMPOSE_CMD exec "$SERVICE" /bin/bash
}

show_help() {
    print_header "Infrastructure Management"
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services (PostgreSQL, Redis, etc.)"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  status      - Show service status"
    echo "  logs        - Show service logs"
    echo "  logs <svc>  - Show logs for specific service"
    echo "  clean       - Remove containers and volumes (WARNING: destructive)"
    echo "  build       - Build/rebuild Docker images"
    echo "  shell [svc] - Open shell in service (default: web)"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs redis"
    echo "  $0 shell web"
}

# -- Main Script --
cd "$PROJECT_ROOT"

case "${1:-}" in
    start)
        docker_start
        ;;
    stop)
        docker_stop
        ;;
    restart)
        docker_restart
        ;;
    status)
        docker_status
        ;;
    logs)
        shift
        docker_logs "$@"
        ;;
    clean)
        docker_clean
        ;;
    build)
        docker_build
        ;;
    shell)
        shift
        docker_shell "$@"
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
