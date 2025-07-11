"""
Model loading module for Unsloth-optimized models.

This module provides functionality for loading models and tokenizers
with Unsloth optimizations and LoRA adapters.
"""

import logging
import torch
from typing import Tuple, Optional
from unsloth import FastLanguageModel, FastModel

from .models import ModelConfig, LoRAConfig

logger = logging.getLogger(__name__)


def load_model_and_tokenizer(
    model_config: ModelConfig,
    lora_config: LoRAConfig
) -> Tuple[FastLanguageModel, any]:
    """
    Load model and tokenizer with Unsloth optimizations.
    
    Args:
        model_config: Model configuration
        lora_config: LoRA configuration
    
    Returns:
        Tuple[FastLanguageModel, any]: Model and tokenizer
    """
    logger.info(f"Loading model: {model_config.model_id}")
    
    try:
        # Determine which FastModel class to use based on model type
        if _is_vision_model(model_config.model_id):
            model, tokenizer = _load_vision_model(model_config)
        else:
            model, tokenizer = _load_language_model(model_config)
        
        # Add LoRA adapters
        model = _add_lora_adapters(model, lora_config)
        
        logger.info("Model and tokenizer loaded successfully")
        return model, tokenizer
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise


def _is_vision_model(model_id: str) -> bool:
    """Check if model is a vision model"""
    vision_keywords = ["vision", "llava", "qwen-vl", "llama-vision"]
    return any(keyword in model_id.lower() for keyword in vision_keywords)


def _load_language_model(model_config: ModelConfig) -> Tuple[FastLanguageModel, any]:
    """Load language model with Unsloth optimizations"""
    logger.info("Loading language model")
    
    # Check if we should use FastLanguageModel or FastModel
    if _should_use_fast_language_model(model_config.model_id):
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_config.model_id,
            max_seq_length=model_config.max_seq_length,
            load_in_4bit=model_config.load_in_4bit,
            fast_inference=model_config.fast_inference,
            max_lora_rank=lora_config.r if hasattr(lora_config, 'r') else 64,
            gpu_memory_utilization=model_config.gpu_memory_utilization,
            token=model_config.token,
        )
    else:
        model, tokenizer = FastModel.from_pretrained(
            model_name=model_config.model_id,
            max_seq_length=model_config.max_seq_length,
            load_in_4bit=model_config.load_in_4bit,
            load_in_8bit=model_config.load_in_8bit,
            full_finetuning=model_config.full_finetuning,
            token=model_config.token,
        )
    
    return model, tokenizer


def _load_vision_model(model_config: ModelConfig) -> Tuple[FastLanguageModel, any]:
    """Load vision model with Unsloth optimizations"""
    logger.info("Loading vision model")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_config.model_id,
        max_seq_length=model_config.max_seq_length,
        load_in_4bit=model_config.load_in_4bit,
        fast_inference=model_config.fast_inference,
        max_lora_rank=lora_config.r if hasattr(lora_config, 'r') else 64,
        gpu_memory_utilization=model_config.gpu_memory_utilization,
        token=model_config.token,
    )
    
    return model, tokenizer


def _should_use_fast_language_model(model_id: str) -> bool:
    """Determine if we should use FastLanguageModel vs FastModel"""
    # Models that work better with FastLanguageModel
    fast_language_models = [
        "llama", "llama-3", "llama-3.1", "llama-3.2", "llama-3.3",
        "mistral", "qwen", "qwen2", "qwen2.5", "deepseek",
        "phi", "gemma", "gemma-3"
    ]
    
    return any(model_type in model_id.lower() for model_type in fast_language_models)


def _add_lora_adapters(model: FastLanguageModel, lora_config: LoRAConfig) -> FastLanguageModel:
    """Add LoRA adapters to the model"""
    logger.info("Adding LoRA adapters")
    
    # Determine which get_peft_model method to use
    if hasattr(model, 'get_peft_model'):
        # FastLanguageModel
        model = model.get_peft_model(
            r=lora_config.r,
            target_modules=lora_config.target_modules,
            lora_alpha=lora_config.lora_alpha,
            use_gradient_checkpointing=lora_config.use_gradient_checkpointing,
            random_state=lora_config.random_state if hasattr(lora_config, 'random_state') else 3407,
        )
    else:
        # FastModel
        model = FastModel.get_peft_model(
            model,
            finetune_vision_layers=lora_config.finetune_vision_layers,
            finetune_language_layers=lora_config.finetune_language_layers,
            finetune_attention_modules=lora_config.finetune_attention_modules,
            finetune_mlp_modules=lora_config.finetune_mlp_modules,
            r=lora_config.r,
            lora_alpha=lora_config.lora_alpha,
            lora_dropout=lora_config.lora_dropout,
            bias=lora_config.bias,
            random_state=lora_config.random_state if hasattr(lora_config, 'random_state') else 3407,
        )
    
    logger.info("LoRA adapters added successfully")
    return model


def get_model_info(model_id: str) -> dict:
    """
    Get information about a model.
    
    Args:
        model_id: Hugging Face model ID
    
    Returns:
        dict: Model information
    """
    # This would typically query Hugging Face Hub API
    # For now, return basic info based on model ID
    info = {
        "model_id": model_id,
        "is_vision": _is_vision_model(model_id),
        "recommended_max_seq_length": 2048,
        "recommended_lora_rank": 8,
    }
    
    # Add model-specific recommendations
    if "gemma" in model_id.lower():
        info.update({
            "recommended_max_seq_length": 1024,
            "recommended_lora_rank": 8,
            "recommended_learning_rate": 5e-6,
        })
    elif "llama" in model_id.lower():
        info.update({
            "recommended_max_seq_length": 2048,
            "recommended_lora_rank": 64,
            "recommended_learning_rate": 5e-6,
        })
    elif "qwen" in model_id.lower():
        info.update({
            "recommended_max_seq_length": 2048,
            "recommended_lora_rank": 32,
            "recommended_learning_rate": 5e-6,
        })
    
    return info


def estimate_memory_usage(
    model_id: str,
    max_seq_length: int,
    batch_size: int,
    load_in_4bit: bool = False,
    load_in_8bit: bool = False
) -> dict:
    """
    Estimate memory usage for a model configuration.
    
    Args:
        model_id: Hugging Face model ID
        max_seq_length: Maximum sequence length
        batch_size: Batch size
        load_in_4bit: Whether to use 4-bit quantization
        load_in_8bit: Whether to use 8-bit quantization
    
    Returns:
        dict: Memory usage estimates
    """
    # Rough estimates based on model size and configuration
    # These are approximate and should be refined with actual measurements
    
    # Base model sizes (in GB)
    model_sizes = {
        "1b": 2.0,
        "3b": 6.0,
        "4b": 8.0,
        "7b": 14.0,
        "8b": 16.0,
        "12b": 24.0,
        "27b": 54.0,
        "70b": 140.0,
    }
    
    # Extract model size from ID
    model_size = None
    for size in model_sizes.keys():
        if size in model_id.lower():
            model_size = size
            break
    
    if model_size is None:
        # Default to 7B if size can't be determined
        model_size = "7b"
    
    base_memory = model_sizes[model_size]
    
    # Apply quantization
    if load_in_4bit:
        base_memory *= 0.25
    elif load_in_8bit:
        base_memory *= 0.5
    
    # Add memory for activations and gradients
    activation_memory = (max_seq_length * batch_size * 2) / (1024 * 1024 * 1024)  # GB
    gradient_memory = base_memory * 0.1  # Rough estimate
    
    total_memory = base_memory + activation_memory + gradient_memory
    
    return {
        "base_model_memory_gb": base_memory,
        "activation_memory_gb": activation_memory,
        "gradient_memory_gb": gradient_memory,
        "total_memory_gb": total_memory,
        "recommended_gpu_memory_gb": total_memory * 1.2,  # 20% buffer
    }


def check_gpu_compatibility(model_config: ModelConfig) -> dict:
    """
    Check if the model configuration is compatible with available GPU.
    
    Args:
        model_config: Model configuration
    
    Returns:
        dict: Compatibility information
    """
    if not torch.cuda.is_available():
        return {
            "compatible": False,
            "reason": "CUDA not available",
            "recommendations": ["Use CPU-only mode", "Install CUDA drivers"]
        }
    
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
    memory_estimate = estimate_memory_usage(
        model_config.model_id,
        model_config.max_seq_length,
        model_config.training.per_device_train_batch_size if hasattr(model_config, 'training') else 1,
        model_config.load_in_4bit,
        model_config.load_in_8bit
    )
    
    required_memory = memory_estimate["recommended_gpu_memory_gb"]
    compatible = gpu_memory >= required_memory
    
    recommendations = []
    if not compatible:
        recommendations.extend([
            "Reduce max_seq_length",
            "Use 4-bit quantization",
            "Reduce batch size",
            "Use gradient accumulation"
        ])
    
    return {
        "compatible": compatible,
        "available_gpu_memory_gb": gpu_memory,
        "required_memory_gb": required_memory,
        "memory_estimate": memory_estimate,
        "recommendations": recommendations
    }