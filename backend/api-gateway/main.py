"""
FastAPI API Gateway for the Train-Your-Own-LLM Platform.

This service provides the main API interface for the platform, handling
training requests, model management, and user interactions.
"""

import os
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Add core package to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.unsloth_trainer import run_grpo, get_available_models, get_recommended_config
from core.unsloth_trainer.models import TrainConfig, RunHandle
from core.unsloth_trainer.utils import validate_config, estimate_training_time, format_config_summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# In-memory storage for demo (replace with database in production)
training_runs: Dict[str, RunHandle] = {}
user_projects: Dict[str, List[str]] = {}


class TrainingRequest(BaseModel):
    """Request model for starting a training run"""
    model_id: str
    dataset_uri: str
    max_steps: Optional[int] = 50
    max_samples: Optional[int] = 1000
    learning_rate: Optional[float] = 5e-6
    lora_rank: Optional[int] = 8
    max_seq_length: Optional[int] = 1024
    reward_types: Optional[List[str]] = None
    project_name: Optional[str] = "Default Project"


class TrainingResponse(BaseModel):
    """Response model for training requests"""
    run_id: str
    status: str
    message: str
    estimated_time_minutes: Optional[float] = None


class RunStatusResponse(BaseModel):
    """Response model for run status"""
    run_id: str
    status: str
    created_at: str
    metrics: Optional[Dict[str, Any]] = None
    logs: Optional[List[str]] = None
    artifacts: Optional[Dict[str, str]] = None


class ModelInfo(BaseModel):
    """Model information response"""
    id: str
    name: str
    family: str
    type: str
    recommended_max_seq_length: int
    recommended_lora_rank: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting API Gateway...")
    yield
    logger.info("Shutting down API Gateway...")


# Create FastAPI app
app = FastAPI(
    title="Train-Your-Own-LLM Platform API",
    description="Production-grade platform for fine-tuning Large Language Models using Unsloth GRPO",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from token (simplified for demo)"""
    # In production, validate JWT token and extract user ID
    # For demo, just return a user ID based on token
    return f"user_{hash(credentials.credentials) % 1000}"


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Train-Your-Own-LLM Platform API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0"
    )


@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """Get list of available models"""
    try:
        models = get_available_models()
        return [ModelInfo(**model) for model in models]
    except Exception as e:
        logger.error(f"Failed to get models: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get models")


@app.get("/models/{model_id}/recommendations")
async def get_model_recommendations(model_id: str, dataset_uri: str = "openai/gsm8k"):
    """Get recommended configuration for a model and dataset"""
    try:
        recommendations = get_recommended_config(model_id, dataset_uri)
        return {
            "model_id": model_id,
            "dataset_uri": dataset_uri,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Failed to get recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


@app.post("/training/start", response_model=TrainingResponse)
async def start_training(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Start a new training run"""
    try:
        # Generate run ID
        run_id = str(uuid.uuid4())
        
        # Create training configuration
        config_kwargs = {
            "max_steps": request.max_steps,
            "max_samples": request.max_samples,
            "learning_rate": request.learning_rate,
            "lora_rank": request.lora_rank,
            "max_seq_length": request.max_seq_length,
        }
        
        if request.reward_types:
            config_kwargs["reward_types"] = request.reward_types
        
        # Validate configuration
        from core.unsloth_trainer.utils import create_default_config
        config = create_default_config(
            model_id=request.model_id,
            dataset_uri=request.dataset_uri,
            **config_kwargs
        )
        validate_config(config)
        
        # Estimate training time
        time_estimate = estimate_training_time(
            model_id=request.model_id,
            dataset_size=request.max_samples or 1000,
            max_steps=request.max_steps or 50,
            batch_size=config.training.per_device_train_batch_size,
            gradient_accumulation_steps=config.training.gradient_accumulation_steps
        )
        
        # Create initial run handle
        run_handle = RunHandle(
            run_id=run_id,
            status="pending",
            created_at=datetime.utcnow().isoformat(),
            config=config,
            metrics=None,
            logs=[],
            artifacts=None
        )
        
        # Store run handle
        training_runs[run_id] = run_handle
        
        # Add to user projects
        if current_user not in user_projects:
            user_projects[current_user] = []
        user_projects[current_user].append(run_id)
        
        # Start training in background
        background_tasks.add_task(run_training, run_id, config)
        
        logger.info(f"Started training run {run_id} for user {current_user}")
        
        return TrainingResponse(
            run_id=run_id,
            status="pending",
            message="Training started successfully",
            estimated_time_minutes=time_estimate["total_time_minutes"]
        )
        
    except Exception as e:
        logger.error(f"Failed to start training: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def run_training(run_id: str, config: TrainConfig):
    """Run training in background"""
    try:
        logger.info(f"Starting training for run {run_id}")
        
        # Update status to running
        if run_id in training_runs:
            training_runs[run_id].status = "running"
        
        # Run training
        result = run_grpo(
            model_id=config.model.model_id,
            dataset_uri=config.dataset.dataset_uri,
            cfg=config
        )
        
        # Update run handle with results
        if run_id in training_runs:
            training_runs[run_id].status = result.status
            training_runs[run_id].metrics = result.metrics
            training_runs[run_id].logs = result.logs
            training_runs[run_id].artifacts = result.artifacts
        
        logger.info(f"Training completed for run {run_id}: {result.status}")
        
    except Exception as e:
        logger.error(f"Training failed for run {run_id}: {str(e)}")
        if run_id in training_runs:
            training_runs[run_id].status = "failed"
            training_runs[run_id].logs = [f"Error: {str(e)}"]


@app.get("/training/runs/{run_id}", response_model=RunStatusResponse)
async def get_run_status(run_id: str, current_user: str = Depends(get_current_user)):
    """Get status of a training run"""
    if run_id not in training_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run_handle = training_runs[run_id]
    
    # Check if user has access to this run
    if current_user not in user_projects or run_id not in user_projects[current_user]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return RunStatusResponse(
        run_id=run_handle.run_id,
        status=run_handle.status,
        created_at=run_handle.created_at,
        metrics=run_handle.metrics,
        logs=run_handle.logs,
        artifacts=run_handle.artifacts
    )


@app.get("/training/runs", response_model=List[RunStatusResponse])
async def list_user_runs(current_user: str = Depends(get_current_user)):
    """Get all training runs for the current user"""
    user_run_ids = user_projects.get(current_user, [])
    runs = []
    
    for run_id in user_run_ids:
        if run_id in training_runs:
            run_handle = training_runs[run_id]
            runs.append(RunStatusResponse(
                run_id=run_handle.run_id,
                status=run_handle.status,
                created_at=run_handle.created_at,
                metrics=run_handle.metrics,
                logs=run_handle.logs,
                artifacts=run_handle.artifacts
            ))
    
    return runs


@app.delete("/training/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_run(run_id: str, current_user: str = Depends(get_current_user)):
    """Cancel a training run"""
    if run_id not in training_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Check if user has access to this run
    if current_user not in user_projects or run_id not in user_projects[current_user]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update status to cancelled
    training_runs[run_id].status = "cancelled"
    
    logger.info(f"Run {run_id} cancelled by user {current_user}")


@app.get("/training/runs/{run_id}/config")
async def get_run_config(run_id: str, current_user: str = Depends(get_current_user)):
    """Get configuration for a training run"""
    if run_id not in training_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Check if user has access to this run
    if current_user not in user_projects or run_id not in user_projects[current_user]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    run_handle = training_runs[run_id]
    
    return {
        "run_id": run_id,
        "config": run_handle.config.dict(),
        "config_summary": format_config_summary(run_handle.config)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)