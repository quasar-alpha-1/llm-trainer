"""
Utility functions for the Unsloth Trainer system.

This module provides helper functions for configuration management,
validation, and common operations.
"""

import logging
from typing import Dict, Any, List, Optional
from .models import (
    TrainConfig, ModelConfig, LoRAConfig, DatasetConfig, 
    TrainingConfig, RewardConfig, RewardFunctionType, ModelType
)

logger = logging.getLogger(__name__)


def create_default_config(
    model_id: str,
    dataset_uri: str,
    **kwargs
) -> TrainConfig:
    """
    Create a default training configuration.
    
    Args:
        model_id: Hugging Face model ID
        dataset_uri: Dataset URI
        **kwargs: Additional configuration parameters
    
    Returns:
        TrainConfig: Default configuration
    """
    # Create model configuration
    model_config = ModelConfig(
        model_id=model_id,
        max_seq_length=kwargs.get('max_seq_length', 1024),
        load_in_4bit=kwargs.get('load_in_4bit', False),
        load_in_8bit=kwargs.get('load_in_8bit', False),
        full_finetuning=kwargs.get('full_finetuning', False),
        fast_inference=kwargs.get('fast_inference', True),
        gpu_memory_utilization=kwargs.get('gpu_memory_utilization', 0.6),
        token=kwargs.get('token'),
    )
    
    # Create LoRA configuration
    lora_config = LoRAConfig(
        r=kwargs.get('lora_rank', 8),
        lora_alpha=kwargs.get('lora_alpha', 8),
        lora_dropout=kwargs.get('lora_dropout', 0.0),
        bias=kwargs.get('bias', "none"),
        target_modules=kwargs.get('target_modules'),
        finetune_vision_layers=kwargs.get('finetune_vision_layers', False),
        finetune_language_layers=kwargs.get('finetune_language_layers', True),
        finetune_attention_modules=kwargs.get('finetune_attention_modules', True),
        finetune_mlp_modules=kwargs.get('finetune_mlp_modules', True),
        use_gradient_checkpointing=kwargs.get('use_gradient_checkpointing', "unsloth"),
    )
    
    # Create dataset configuration
    dataset_config = DatasetConfig(
        dataset_uri=dataset_uri,
        dataset_type=kwargs.get('dataset_type', 'huggingface'),
        split=kwargs.get('split', 'train'),
        max_samples=kwargs.get('max_samples'),
        system_prompt=kwargs.get('system_prompt'),
        user_prompt_column=kwargs.get('user_prompt_column', 'question'),
        answer_column=kwargs.get('answer_column', 'answer'),
        reasoning_start=kwargs.get('reasoning_start', '<start_working_out>'),
        reasoning_end=kwargs.get('reasoning_end', '<end_working_out>'),
        solution_start=kwargs.get('solution_start', '<SOLUTION>'),
        solution_end=kwargs.get('solution_end', '</SOLUTION>'),
    )
    
    # Create reward configurations
    reward_types = kwargs.get('reward_types', ['format_match', 'format_approximate', 'answer_check', 'number_check'])
    rewards = []
    
    for reward_type in reward_types:
        if isinstance(reward_type, str):
            try:
                reward_type_enum = RewardFunctionType(reward_type)
                rewards.append(RewardConfig(
                    reward_type=reward_type_enum,
                    weight=kwargs.get('reward_weights', {}).get(reward_type, 1.0),
                    parameters=kwargs.get('reward_parameters', {}).get(reward_type, {})
                ))
            except ValueError:
                logger.warning(f"Unknown reward type: {reward_type}")
        elif isinstance(reward_type, dict):
            rewards.append(RewardConfig(**reward_type))
    
    # Create training configuration
    training_config = TrainingConfig(
        learning_rate=kwargs.get('learning_rate', 5e-6),
        adam_beta1=kwargs.get('adam_beta1', 0.9),
        adam_beta2=kwargs.get('adam_beta2', 0.99),
        weight_decay=kwargs.get('weight_decay', 0.1),
        warmup_ratio=kwargs.get('warmup_ratio', 0.1),
        lr_scheduler_type=kwargs.get('lr_scheduler_type', 'cosine'),
        optim=kwargs.get('optim', 'adamw_torch_fused'),
        logging_steps=kwargs.get('logging_steps', 1),
        per_device_train_batch_size=kwargs.get('per_device_train_batch_size', 1),
        gradient_accumulation_steps=kwargs.get('gradient_accumulation_steps', 1),
        num_generations=kwargs.get('num_generations', 4),
        max_prompt_length=kwargs.get('max_prompt_length', 256),
        max_completion_length=kwargs.get('max_completion_length'),
        num_train_epochs=kwargs.get('num_train_epochs'),
        max_steps=kwargs.get('max_steps'),
        save_steps=kwargs.get('save_steps', 50),
        max_grad_norm=kwargs.get('max_grad_norm', 0.1),
        report_to=kwargs.get('report_to', 'none'),
        output_dir=kwargs.get('output_dir', 'outputs'),
    )
    
    # Create complete configuration
    config = TrainConfig(
        model=model_config,
        lora=lora_config,
        dataset=dataset_config,
        rewards=rewards,
        training=training_config,
        random_state=kwargs.get('random_state', 3407),
    )
    
    return config


def validate_config(config: TrainConfig) -> None:
    """
    Validate training configuration.
    
    Args:
        config: Training configuration to validate
    
    Raises:
        ValueError: If configuration is invalid
    """
    logger.info("Validating training configuration")
    
    # Validate model configuration
    if not config.model.model_id:
        raise ValueError("Model ID is required")
    
    if config.model.max_seq_length < 512:
        raise ValueError("max_seq_length must be at least 512")
    
    if config.model.max_seq_length > 8192:
        raise ValueError("max_seq_length must be at most 8192")
    
    # Validate LoRA configuration
    if config.lora.r < 1:
        raise ValueError("LoRA rank must be at least 1")
    
    if config.lora.r > 256:
        raise ValueError("LoRA rank must be at most 256")
    
    if config.lora.lora_alpha < 1:
        raise ValueError("LoRA alpha must be at least 1")
    
    # Validate dataset configuration
    if not config.dataset.dataset_uri:
        raise ValueError("Dataset URI is required")
    
    if config.dataset.max_samples is not None and config.dataset.max_samples < 1:
        raise ValueError("max_samples must be at least 1")
    
    # Validate training configuration
    if config.training.learning_rate <= 0:
        raise ValueError("Learning rate must be positive")
    
    if config.training.learning_rate > 1e-3:
        raise ValueError("Learning rate must be at most 1e-3")
    
    if config.training.per_device_train_batch_size < 1:
        raise ValueError("Batch size must be at least 1")
    
    if config.training.num_generations < 1:
        raise ValueError("Number of generations must be at least 1")
    
    if config.training.num_generations > 16:
        raise ValueError("Number of generations must be at most 16")
    
    # Validate reward functions
    if not config.rewards:
        raise ValueError("At least one reward function is required")
    
    for reward in config.rewards:
        if reward.weight < 0:
            raise ValueError("Reward weight must be non-negative")
    
    logger.info("Configuration validation passed")


def get_available_models() -> List[Dict[str, Any]]:
    """
    Get list of available models.
    
    Returns:
        List[Dict[str, Any]]: List of model information
    """
    models = []
    
    for model_type in ModelType:
        model_info = {
            "id": model_type.value,
            "name": model_type.name,
            "type": "language" if "vision" not in model_type.value.lower() else "vision",
        }
        
        # Add model-specific information
        if "gemma" in model_type.value.lower():
            model_info.update({
                "family": "Gemma",
                "recommended_max_seq_length": 1024,
                "recommended_lora_rank": 8,
            })
        elif "llama" in model_type.value.lower():
            model_info.update({
                "family": "Llama",
                "recommended_max_seq_length": 2048,
                "recommended_lora_rank": 64,
            })
        elif "qwen" in model_type.value.lower():
            model_info.update({
                "family": "Qwen",
                "recommended_max_seq_length": 2048,
                "recommended_lora_rank": 32,
            })
        elif "mistral" in model_type.value.lower():
            model_info.update({
                "family": "Mistral",
                "recommended_max_seq_length": 2048,
                "recommended_lora_rank": 32,
            })
        elif "phi" in model_type.value.lower():
            model_info.update({
                "family": "Phi",
                "recommended_max_seq_length": 2048,
                "recommended_lora_rank": 16,
            })
        elif "deepseek" in model_type.value.lower():
            model_info.update({
                "family": "DeepSeek",
                "recommended_max_seq_length": 2048,
                "recommended_lora_rank": 32,
            })
        
        models.append(model_info)
    
    return models


def get_recommended_config(model_id: str, dataset_uri: str) -> Dict[str, Any]:
    """
    Get recommended configuration for a model and dataset.
    
    Args:
        model_id: Hugging Face model ID
        dataset_uri: Dataset URI
    
    Returns:
        Dict[str, Any]: Recommended configuration
    """
    recommendations = {
        "model": {
            "max_seq_length": 1024,
            "load_in_4bit": False,
            "load_in_8bit": False,
            "full_finetuning": False,
        },
        "lora": {
            "r": 8,
            "lora_alpha": 8,
            "lora_dropout": 0.0,
        },
        "training": {
            "learning_rate": 5e-6,
            "per_device_train_batch_size": 1,
            "gradient_accumulation_steps": 1,
            "num_generations": 4,
            "max_steps": 50,
        },
        "rewards": ["format_match", "format_approximate", "answer_check", "number_check"]
    }
    
    # Model-specific recommendations
    if "gemma" in model_id.lower():
        recommendations["model"]["max_seq_length"] = 1024
        recommendations["lora"]["r"] = 8
        recommendations["training"]["learning_rate"] = 5e-6
    elif "llama" in model_id.lower():
        recommendations["model"]["max_seq_length"] = 2048
        recommendations["lora"]["r"] = 64
        recommendations["training"]["learning_rate"] = 5e-6
    elif "qwen" in model_id.lower():
        recommendations["model"]["max_seq_length"] = 2048
        recommendations["lora"]["r"] = 32
        recommendations["training"]["learning_rate"] = 5e-6
    elif "mistral" in model_id.lower():
        recommendations["model"]["max_seq_length"] = 2048
        recommendations["lora"]["r"] = 32
        recommendations["training"]["learning_rate"] = 5e-6
    
    # Dataset-specific recommendations
    if "gsm8k" in dataset_uri.lower():
        recommendations["rewards"] = ["format_match", "format_approximate", "answer_check", "number_check"]
    elif "math" in dataset_uri.lower():
        recommendations["rewards"] = ["format_match", "number_check"]
    else:
        recommendations["rewards"] = ["format_match", "format_approximate"]
    
    return recommendations


def estimate_training_time(
    model_id: str,
    dataset_size: int,
    max_steps: int,
    batch_size: int,
    gradient_accumulation_steps: int
) -> Dict[str, Any]:
    """
    Estimate training time for a configuration.
    
    Args:
        model_id: Hugging Face model ID
        dataset_size: Number of samples in dataset
        max_steps: Maximum training steps
        batch_size: Batch size
        gradient_accumulation_steps: Gradient accumulation steps
    
    Returns:
        Dict[str, Any]: Time estimates
    """
    # Rough estimates based on model size and configuration
    # These are approximate and should be refined with actual measurements
    
    # Base time per step (in seconds) for different model sizes
    base_times = {
        "1b": 2.0,
        "3b": 4.0,
        "4b": 5.0,
        "7b": 8.0,
        "8b": 10.0,
        "12b": 15.0,
        "27b": 30.0,
        "70b": 60.0,
    }
    
    # Extract model size from ID
    model_size = None
    for size in base_times.keys():
        if size in model_id.lower():
            model_size = size
            break
    
    if model_size is None:
        model_size = "7b"  # Default
    
    base_time_per_step = base_times[model_size]
    
    # Adjust for batch size and gradient accumulation
    effective_batch_size = batch_size * gradient_accumulation_steps
    time_per_step = base_time_per_step * (effective_batch_size / 1)  # Normalize to batch size 1
    
    # Calculate total time
    total_time_seconds = time_per_step * max_steps
    total_time_minutes = total_time_seconds / 60
    total_time_hours = total_time_minutes / 60
    
    # Calculate epochs
    steps_per_epoch = dataset_size // effective_batch_size
    if steps_per_epoch == 0:
        steps_per_epoch = 1
    
    epochs = max_steps / steps_per_epoch
    
    return {
        "time_per_step_seconds": time_per_step,
        "total_time_seconds": total_time_seconds,
        "total_time_minutes": total_time_minutes,
        "total_time_hours": total_time_hours,
        "steps_per_epoch": steps_per_epoch,
        "epochs": epochs,
        "effective_batch_size": effective_batch_size,
    }


def format_config_summary(config: TrainConfig) -> str:
    """
    Format configuration as a human-readable summary.
    
    Args:
        config: Training configuration
    
    Returns:
        str: Formatted summary
    """
    summary = f"""
Training Configuration Summary
==============================

Model: {config.model.model_id}
- Max sequence length: {config.model.max_seq_length}
- 4-bit quantization: {config.model.load_in_4bit}
- 8-bit quantization: {config.model.load_in_8bit}
- Full fine-tuning: {config.model.full_finetuning}

LoRA Configuration:
- Rank: {config.lora.r}
- Alpha: {config.lora.lora_alpha}
- Dropout: {config.lora.lora_dropout}

Dataset: {config.dataset.dataset_uri}
- Type: {config.dataset.dataset_type}
- Split: {config.dataset.split}
- Max samples: {config.dataset.max_samples or 'All'}

Training Parameters:
- Learning rate: {config.training.learning_rate}
- Batch size: {config.training.per_device_train_batch_size}
- Gradient accumulation: {config.training.gradient_accumulation_steps}
- Max steps: {config.training.max_steps or 'Not set'}
- Epochs: {config.training.num_train_epochs or 'Not set'}

Reward Functions: {len(config.rewards)}
"""
    
    for i, reward in enumerate(config.rewards, 1):
        summary += f"- {i}. {reward.reward_type.value} (weight: {reward.weight})\n"
    
    return summary