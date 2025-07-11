#!/bin/bash

# LLM Trainer Platform Local Development Script

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

# Function to check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ and try again."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
        print_error "Python 3.8+ is required. Current version: $python_version"
        exit 1
    fi
}

# Function to check if Node.js is available
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ and try again."
        exit 1
    fi
    
    node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ $node_version -lt 18 ]]; then
        print_error "Node.js 18+ is required. Current version: $(node --version)"
        exit 1
    fi
}

# Function to install backend dependencies
install_backend_deps() {
    print_status "Installing backend dependencies..."
    
    if [ ! -d "backend/api-gateway" ]; then
        print_error "Backend directory not found!"
        exit 1
    fi
    
    cd backend/api-gateway
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    cd ../..
    print_success "Backend dependencies installed!"
}

# Function to install frontend dependencies
install_frontend_deps() {
    print_status "Installing frontend dependencies..."
    
    if [ ! -d "frontend" ]; then
        print_error "Frontend directory not found!"
        exit 1
    fi
    
    cd frontend
    
    # Install dependencies
    npm install
    
    cd ..
    print_success "Frontend dependencies installed!"
}

# Function to start backend
start_backend() {
    print_status "Starting backend API server..."
    
    cd backend/api-gateway
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start the server
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ../..
    
    print_success "Backend started with PID: $BACKEND_PID"
    echo $BACKEND_PID > .backend.pid
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend development server..."
    
    cd frontend
    
    # Start the development server
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    print_success "Frontend started with PID: $FRONTEND_PID"
    echo $FRONTEND_PID > .frontend.pid
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_status "Backend stopped"
        fi
        rm -f .backend.pid
    fi
    
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_status "Frontend stopped"
        fi
        rm -f .frontend.pid
    fi
    
    print_success "All services stopped!"
}

# Function to show status
show_status() {
    print_status "Service Status:"
    
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "  Backend: Running (PID: $BACKEND_PID)"
        else
            echo "  Backend: Not running"
            rm -f .backend.pid
        fi
    else
        echo "  Backend: Not running"
    fi
    
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "  Frontend: Running (PID: $FRONTEND_PID)"
        else
            echo "  Frontend: Not running"
            rm -f .frontend.pid
        fi
    else
        echo "  Frontend: Not running"
    fi
}

# Function to show help
show_help() {
    echo "LLM Trainer Platform Local Development Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Install all dependencies"
    echo "  start       Start the platform (default)"
    echo "  stop        Stop the platform"
    echo "  restart     Restart the platform"
    echo "  status      Show platform status"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install"
    echo "  $0 start"
    echo "  $0 status"
}

# Main script logic
case "${1:-start}" in
    install)
        check_python
        check_node
        install_backend_deps
        install_frontend_deps
        print_success "All dependencies installed!"
        print_status "You can now run: $0 start"
        ;;
    start)
        check_python
        check_node
        
        # Install dependencies if not already installed
        if [ ! -d "backend/api-gateway/venv" ]; then
            print_warning "Dependencies not installed. Installing now..."
            install_backend_deps
        fi
        
        if [ ! -d "frontend/node_modules" ]; then
            print_warning "Frontend dependencies not installed. Installing now..."
            install_frontend_deps
        fi
        
        # Stop any existing services
        stop_services
        
        # Start services
        start_backend
        sleep 3  # Give backend time to start
        start_frontend
        
        print_success "Platform started successfully!"
        print_status "Services available at:"
        echo "  - Frontend: http://localhost:3000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo ""
        print_status "Press Ctrl+C to stop all services"
        
        # Wait for user to stop
        wait
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        $0 start
        ;;
    status)
        show_status
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