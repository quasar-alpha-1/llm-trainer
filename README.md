# LLM Trainer Platform

A comprehensive platform for training and managing Large Language Models (LLMs) with a modern web interface, API gateway, and monitoring capabilities.

## 🚀 Features

- **Modern Web Interface**: React-based frontend with Material-UI components
- **RESTful API**: FastAPI backend with automatic documentation
- **Training Job Management**: Create, monitor, and manage LLM training jobs
- **Model Support**: Pre-configured support for popular models (Gemma, Qwen, Llama, DeepSeek)
- **Dataset Management**: Easy dataset selection and management
- **Monitoring**: Prometheus and Grafana integration for metrics and visualization
- **Object Storage**: MinIO for model and dataset storage
- **Database**: PostgreSQL for persistent data storage
- **Caching**: Redis for performance optimization

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   PostgreSQL    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Database      │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │     Cache       │
                       │   Port: 6379    │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     MinIO       │
                       │ Object Storage  │
                       │ Port: 9000/9001 │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Prometheus    │
                       │   Monitoring    │
                       │   Port: 9090    │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Grafana      │
                       │   Dashboard     │
                       │   Port: 3001    │
                       └─────────────────┘
```

## 🛠️ Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd llm-trainer
   ```

2. **Start the platform**:
   ```bash
   ./dev.sh start
   ```

3. **Access the services**:
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001
   - Grafana Dashboard: http://localhost:3001
   - Prometheus: http://localhost:9090

### Local Development

1. **Install dependencies**:
   ```bash
   ./dev.sh install
   ```

2. **Start services individually**:
   ```bash
   # Start backend
   cd backend/api-gateway
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Start frontend (in another terminal)
   cd frontend
   npm install
   npm start
   ```

## 📋 Available Commands

```bash
./dev.sh start      # Start the platform
./dev.sh stop       # Stop the platform
./dev.sh restart    # Restart the platform
./dev.sh logs       # Show logs
./dev.sh status     # Show platform status
./dev.sh install    # Install dependencies locally
./dev.sh test       # Run tests
./dev.sh cleanup    # Remove all containers and volumes
./dev.sh help       # Show help
```

## 🎯 Usage

### Creating a Training Job

1. Open the frontend at http://localhost:3000
2. Select a model from the dropdown (e.g., Gemma3-1B, Qwen3-4B)
3. Choose a dataset (e.g., Alpaca, Dolly, Code-Alpaca)
4. Configure hyperparameters:
   - Learning Rate: 0.001 (default)
   - Batch Size: 4 (default)
   - Epochs: 3 (default)
5. Click "Start Training"

### Monitoring Training Jobs

- View all training jobs in the dashboard
- Check job status (pending, running, completed, failed)
- Monitor training progress and metrics
- Access detailed logs and performance data

### API Usage

The API provides RESTful endpoints for programmatic access:

```bash
# Get all training jobs
curl http://localhost:8000/api/jobs

# Create a new training job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "gemma3-1b",
    "dataset_path": "alpaca",
    "hyperparameters": {
      "learning_rate": 0.001,
      "batch_size": 4,
      "epochs": 3
    }
  }'

# Get available models
curl http://localhost:8000/api/models

# Get available datasets
curl http://localhost:8000/api/datasets
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/llm_trainer

# Redis
REDIS_URL=redis://redis:6379

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Grafana
GF_SECURITY_ADMIN_PASSWORD=admin
```

### Custom Models

To add custom models, modify the `get_available_models()` function in `backend/api-gateway/main.py`:

```python
@app.get("/api/models")
async def get_available_models():
    models = [
        {"name": "your-custom-model", "type": "transformer", "parameters": "7B"},
        # ... existing models
    ]
    return models
```

## 📊 Monitoring

### Prometheus Metrics

The platform exposes metrics at `/metrics` endpoint for Prometheus scraping.

### Grafana Dashboards

Access Grafana at http://localhost:3001 with:
- Username: `admin`
- Password: `admin`

Pre-configured dashboards include:
- Training job metrics
- System resource usage
- API performance metrics

## 🧪 Testing

Run tests using the development script:

```bash
./dev.sh test
```

Or run tests individually:

```bash
# Backend tests
cd backend/api-gateway
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000, 8000, 5432, 6379, 9000, 9001, 9090, and 3001 are available
2. **Docker not running**: Start Docker Desktop or Docker daemon
3. **Permission issues**: Ensure the `dev.sh` script is executable (`chmod +x dev.sh`)

### Logs

View logs for debugging:

```bash
# All services
./dev.sh logs

# Specific service
./dev.sh logs api-gateway
./dev.sh logs frontend
```

### Reset Platform

To completely reset the platform:

```bash
./dev.sh cleanup
./dev.sh start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React and Material-UI for the frontend components
- Docker for containerization
- Prometheus and Grafana for monitoring
- The open-source LLM community for inspiration

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the documentation at http://localhost:8000/docs
- Review the logs using `./dev.sh logs`

---

**Happy Training! 🚀**