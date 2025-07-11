from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from datetime import datetime
import json

app = FastAPI(
    title="LLM Trainer API",
    description="API for training and managing Large Language Models",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TrainingJob(BaseModel):
    id: str
    model_name: str
    dataset_path: str
    hyperparameters: dict
    status: str = "pending"
    created_at: datetime
    updated_at: datetime

class CreateTrainingJob(BaseModel):
    model_name: str
    dataset_path: str
    hyperparameters: dict

# In-memory storage (replace with database in production)
training_jobs = {}

@app.get("/")
async def root():
    return {"message": "LLM Trainer API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/jobs", response_model=List[TrainingJob])
async def get_training_jobs():
    """Get all training jobs"""
    return list(training_jobs.values())

@app.get("/api/jobs/{job_id}", response_model=TrainingJob)
async def get_training_job(job_id: str):
    """Get a specific training job"""
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    return training_jobs[job_id]

@app.post("/api/jobs", response_model=TrainingJob)
async def create_training_job(job: CreateTrainingJob):
    """Create a new training job"""
    job_id = f"job_{len(training_jobs) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    training_job = TrainingJob(
        id=job_id,
        model_name=job.model_name,
        dataset_path=job.dataset_path,
        hyperparameters=job.hyperparameters,
        status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    training_jobs[job_id] = training_job
    return training_job

@app.put("/api/jobs/{job_id}/status")
async def update_job_status(job_id: str, status: str):
    """Update training job status"""
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    training_jobs[job_id].status = status
    training_jobs[job_id].updated_at = datetime.now()
    return {"message": "Status updated successfully"}

@app.get("/api/models")
async def get_available_models():
    """Get list of available models for training"""
    models = [
        {"name": "gemma3-1b", "type": "transformer", "parameters": "1B"},
        {"name": "qwen3-4b", "type": "transformer", "parameters": "4B"},
        {"name": "llama3-2-3b", "type": "transformer", "parameters": "3B"},
        {"name": "deepseek-r1-8b", "type": "transformer", "parameters": "8B"}
    ]
    return models

@app.get("/api/datasets")
async def get_available_datasets():
    """Get list of available datasets"""
    datasets = [
        {"name": "alpaca", "type": "instruction", "size": "52K"},
        {"name": "dolly", "type": "instruction", "size": "15K"},
        {"name": "code-alpaca", "type": "code", "size": "20K"}
    ]
    return datasets

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)