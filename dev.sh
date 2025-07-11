#!/bin/bash

# LLM Trainer Platform Development Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
}

# Function to start the platform
start_platform() {
    print_status "Starting LLM Trainer Platform..."
    
    check_docker
    check_docker_compose
    
    # Build and start services
    docker-compose up -d --build
    
    print_success "Platform started successfully!"
    print_status "Services available at:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - MinIO Console: http://localhost:9001"
    echo "  - Grafana: http://localhost:3001"
    echo "  - Prometheus: http://localhost:9090"
}

# Function to stop the platform
stop_platform() {
    print_status "Stopping LLM Trainer Platform..."
    docker-compose down
    print_success "Platform stopped successfully!"
}

# Function to restart the platform
restart_platform() {
    print_status "Restarting LLM Trainer Platform..."
    stop_platform
    start_platform
}

# Function to show logs
show_logs() {
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$1"
    fi
}

# Function to show status
show_status() {
    print_status "Platform Status:"
    docker-compose ps
}

# Function to clean up
cleanup() {
    print_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --rmi all
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to install dependencies locally
install_deps() {
    print_status "Installing dependencies..."
    
    # Install backend dependencies
    if [ -d "backend/api-gateway" ]; then
        print_status "Installing backend dependencies..."
        cd backend/api-gateway
        pip install -r requirements.txt
        cd ../..
    fi
    
    # Install frontend dependencies
    if [ -d "frontend" ]; then
        print_status "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
    fi
    
    print_success "Dependencies installed successfully!"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Backend tests
    if [ -d "backend/api-gateway" ]; then
        print_status "Running backend tests..."
        cd backend/api-gateway
        python -m pytest tests/ -v
        cd ../..
    fi
    
    # Frontend tests
    if [ -d "frontend" ]; then
        print_status "Running frontend tests..."
        cd frontend
        npm test -- --watchAll=false
        cd ..
    fi
    
    print_success "Tests completed!"
}

# Function to show help
show_help() {
    echo "LLM Trainer Platform Development Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the platform (default)"
    echo "  stop        Stop the platform"
    echo "  restart     Restart the platform"
    echo "  logs [SERVICE] Show logs (all services or specific service)"
    echo "  status      Show platform status"
    echo "  install     Install dependencies locally"
    echo "  test        Run tests"
    echo "  cleanup     Remove all containers, volumes, and images"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs api-gateway"
    echo "  $0 status"
}

# Main script logic
case "${1:-start}" in
    start)
        start_platform
        ;;
    stop)
        stop_platform
        ;;
    restart)
        restart_platform
        ;;
    logs)
        show_logs "$2"
        ;;
    status)
        show_status
        ;;
    install)
        install_deps
        ;;
    test)
        run_tests
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac