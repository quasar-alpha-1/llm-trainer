#!/bin/bash

# Train-Your-Own-LLM Platform Setup Script
# This script sets up the complete platform for development

set -e

echo "🚀 Setting up Train-Your-Own-LLM Platform..."

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check system requirements
print_status "Checking system requirements..."

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python version: $PYTHON_VERSION"
else
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker version: $DOCKER_VERSION"
else
    print_error "Docker is required but not installed"
    print_status "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker Compose version: $COMPOSE_VERSION"
else
    print_error "Docker Compose is required but not installed"
    print_status "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check NVIDIA Docker (optional)
if command -v nvidia-docker &> /dev/null; then
    print_success "NVIDIA Docker is available"
    NVIDIA_DOCKER_AVAILABLE=true
else
    print_warning "NVIDIA Docker not found. GPU training will not be available."
    print_status "To enable GPU training, install NVIDIA Docker: https://github.com/NVIDIA/nvidia-docker"
    NVIDIA_DOCKER_AVAILABLE=false
fi

# Create necessary directories
print_status "Creating project directories..."
mkdir -p logs
mkdir -p data
mkdir -p outputs
mkdir -p cache

# Set up Python virtual environment
print_status "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
print_status "Installing core dependencies..."
pip install -r core/requirements.txt

# Install backend dependencies
print_status "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create environment file
print_status "Creating environment configuration..."
cat > .env << EOF
# Environment Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database Configuration
POSTGRES_DB=train_platform
POSTGRES_USER=train_user
POSTGRES_PASSWORD=train_password
DATABASE_URL=postgresql://train_user:train_password@localhost:5432/train_platform

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ENDPOINT=localhost:9000

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# Security (change in production)
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Hugging Face (optional)
HUGGINGFACE_TOKEN=

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
EOF

print_success "Environment file created"

# Create Docker configuration files
print_status "Creating Docker configuration files..."

# Create Prometheus configuration
mkdir -p docker
cat > docker/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'

  - job_name: 'trainer-service'
    static_configs:
      - targets: ['trainer-service:8001']
    metrics_path: '/metrics'

  - job_name: 'agent-service'
    static_configs:
      - targets: ['agent-service:8002']
    metrics_path: '/metrics'
EOF

# Create Grafana provisioning
mkdir -p docker/grafana/provisioning/datasources
mkdir -p docker/grafana/provisioning/dashboards

cat > docker/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

cat > docker/grafana/provisioning/dashboards/dashboard.yml << EOF
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

print_success "Docker configuration files created"

# Create development script
print_status "Creating development scripts..."

cat > dev.sh << 'EOF'
#!/bin/bash

# Development script for Train-Your-Own-LLM Platform

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

case "$1" in
    "start")
        print_status "Starting development environment..."
        docker-compose up -d postgres minio redis prometheus grafana
        print_status "Waiting for services to be ready..."
        sleep 10
        print_status "Starting API gateway..."
        cd backend/api-gateway && python main.py &
        cd ../..
        print_status "Starting frontend..."
        cd frontend && npm start &
        cd ..
        print_success "Development environment started!"
        print_status "Frontend: http://localhost:3000"
        print_status "API Docs: http://localhost:8000/docs"
        print_status "MinIO Console: http://localhost:9001"
        print_status "Grafana: http://localhost:3001"
        ;;
    "stop")
        print_status "Stopping development environment..."
        docker-compose down
        pkill -f "python main.py" || true
        pkill -f "npm start" || true
        print_success "Development environment stopped!"
        ;;
    "restart")
        ./dev.sh stop
        sleep 2
        ./dev.sh start
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "clean")
        print_status "Cleaning up..."
        docker-compose down -v
        docker system prune -f
        print_success "Cleanup completed!"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|clean}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the development environment"
        echo "  stop    - Stop the development environment"
        echo "  restart - Restart the development environment"
        echo "  logs    - Show logs from all services"
        echo "  clean   - Clean up all containers and volumes"
        exit 1
        ;;
esac
EOF

chmod +x dev.sh

# Create production script
cat > prod.sh << 'EOF'
#!/bin/bash

# Production script for Train-Your-Own-LLM Platform

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

case "$1" in
    "deploy")
        print_status "Deploying to production..."
        
        # Build frontend
        print_status "Building frontend..."
        cd frontend
        npm run build
        cd ..
        
        # Start all services
        print_status "Starting production services..."
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
        
        print_success "Production deployment completed!"
        ;;
    "stop")
        print_status "Stopping production services..."
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
        print_success "Production services stopped!"
        ;;
    "logs")
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
        ;;
    "backup")
        print_status "Creating backup..."
        BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        
        # Backup database
        docker-compose exec -T postgres pg_dump -U train_user train_platform > $BACKUP_DIR/database.sql
        
        # Backup MinIO data
        docker run --rm -v train-your-own-llm-platform_minio_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/minio_data.tar.gz -C /data .
        
        print_success "Backup created in $BACKUP_DIR"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|logs|backup}"
        echo ""
        echo "Commands:"
        echo "  deploy - Deploy to production"
        echo "  stop   - Stop production services"
        echo "  logs   - Show production logs"
        echo "  backup - Create backup of data"
        exit 1
        ;;
esac
EOF

chmod +x prod.sh

# Create test script
cat > test.sh << 'EOF'
#!/bin/bash

# Test script for Train-Your-Own-LLM Platform

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Activate virtual environment
source venv/bin/activate

print_status "Running tests..."

# Test core package
print_status "Testing core package..."
cd core
python -m pytest tests/ -v
cd ..

# Test backend
print_status "Testing backend..."
cd backend
python -m pytest tests/ -v
cd ..

# Test frontend
print_status "Testing frontend..."
cd frontend
npm test -- --watchAll=false
cd ..

print_success "All tests completed!"
EOF

chmod +x test.sh

# Create example training script
cat > examples/run_example.py << 'EOF'
#!/usr/bin/env python3
"""
Example script to demonstrate the platform usage.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.unsloth_trainer import run_gemma_grpo

def main():
    print("🚀 Running example training...")
    
    # Run a simple training example
    result = run_gemma_grpo(
        model_size="1b",
        dataset_uri="openai/gsm8k",
        max_steps=5,  # Small number for demo
        max_samples=50  # Small dataset for demo
    )
    
    print(f"✅ Training completed!")
    print(f"Run ID: {result.run_id}")
    print(f"Status: {result.status}")
    print(f"Metrics: {result.metrics}")

if __name__ == "__main__":
    main()
EOF

chmod +x examples/run_example.py

print_success "Development scripts created"

# Create README for quick start
cat > QUICKSTART.md << 'EOF'
# Quick Start Guide

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Node.js 16+ (for frontend)
- NVIDIA GPU with CUDA (optional, for GPU training)

## Development Setup

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd train-your-own-llm-platform
   ./setup.sh
   ```

2. **Start development environment:**
   ```bash
   ./dev.sh start
   ```

3. **Access the platform:**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001
   - Grafana: http://localhost:3001

## Production Deployment

1. **Deploy to production:**
   ```bash
   ./prod.sh deploy
   ```

2. **Stop production services:**
   ```bash
   ./prod.sh stop
   ```

## Running Examples

```bash
# Run a simple training example
python examples/run_example.py

# Run the comprehensive examples
python examples/simple_training.py
```

## Testing

```bash
# Run all tests
./test.sh
```

## Troubleshooting

- Check logs: `./dev.sh logs`
- Restart services: `./dev.sh restart`
- Clean environment: `./dev.sh clean`
EOF

print_success "Quick start guide created"

# Final setup steps
print_status "Performing final setup steps..."

# Make sure Docker can run without sudo
if ! docker info &> /dev/null; then
    print_warning "Docker requires sudo. Consider adding your user to the docker group:"
    print_status "sudo usermod -aG docker $USER"
    print_status "Then log out and log back in."
fi

# Test Docker Compose
print_status "Testing Docker Compose..."
docker-compose config > /dev/null
print_success "Docker Compose configuration is valid"

print_success "Setup completed successfully!"
echo ""
echo "🎉 Train-Your-Own-LLM Platform is ready!"
echo ""
echo "Next steps:"
echo "1. Start development environment: ./dev.sh start"
echo "2. Access the platform: http://localhost:3000"
echo "3. Run examples: python examples/run_example.py"
echo "4. Check documentation: README.md"
echo ""
echo "Happy training! 🚀"