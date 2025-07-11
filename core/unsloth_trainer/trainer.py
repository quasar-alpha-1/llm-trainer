"""
Core trainer module that abstracts Unsloth GRPO notebook logic.

This module provides a unified interface for running GRPO training across
different model types and configurations.
"""

import os
import re
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import torch
from datasets import load_dataset, Dataset
from transformers import TextStreamer
from trl import GRPOConfig, GRPOTrainer

from .models import TrainConfig, RunHandle, RewardFunctionType
from .reward_functions import get_reward_functions
from .data_processing import process_dataset
from .model_loading import load_model_and_tokenizer

logger = logging.getLogger(__name__)


class UnslothTrainer:
    """Main trainer class that orchestrates GRPO training"""
    
    def __init__(self, config: TrainConfig):
        """Initialize trainer with configuration"""
        self.config = config
        self.run_id = str(uuid.uuid4())
        self.model = None
        self.tokenizer = None
        self.trainer = None
        self.dataset = None
        
        # Set random seed
        torch.manual_seed(config.random_state)
        
        logger.info(f"Initialized trainer with run_id: {self.run_id}")
    
    def setup(self) -> None:
        """Setup model, tokenizer, and dataset"""
        logger.info("Setting up training environment...")
        
        # Load model and tokenizer
        self.model, self.tokenizer = load_model_and_tokenizer(
            model_config=self.config.model,
            lora_config=self.config.lora
        )
        
        # Process dataset
        self.dataset = process_dataset(
            dataset_config=self.config.dataset,
            tokenizer=self.tokenizer
        )
        
        logger.info("Training environment setup complete")
    
    def create_reward_functions(self) -> List[Callable]:
        """Create reward functions based on configuration"""
        reward_functions = []
        
        for reward_config in self.config.rewards:
            if reward_config.reward_type == RewardFunctionType.CUSTOM:
                # Handle custom reward functions
                if reward_config.custom_code:
                    # TODO: Implement safe execution of custom code
                    logger.warning("Custom reward functions not yet implemented")
                    continue
            else:
                # Get predefined reward function
                reward_func = get_reward_functions(
                    reward_config.reward_type,
                    self.config.dataset,
                    reward_config.parameters or {}
                )
                reward_functions.append(reward_func)
        
        return reward_functions
    
    def create_training_args(self) -> GRPOConfig:
        """Create GRPO training arguments"""
        # Calculate max_completion_length if not provided
        max_completion_length = self.config.training.max_completion_length
        if max_completion_length is None:
            max_completion_length = (
                self.config.model.max_seq_length - 
                self.config.training.max_prompt_length
            )
        
        return GRPOConfig(
            learning_rate=self.config.training.learning_rate,
            adam_beta1=self.config.training.adam_beta1,
            adam_beta2=self.config.training.adam_beta2,
            weight_decay=self.config.training.weight_decay,
            warmup_ratio=self.config.training.warmup_ratio,
            lr_scheduler_type=self.config.training.lr_scheduler_type,
            optim=self.config.training.optim,
            logging_steps=self.config.training.logging_steps,
            per_device_train_batch_size=self.config.training.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.training.gradient_accumulation_steps,
            num_generations=self.config.training.num_generations,
            max_prompt_length=self.config.training.max_prompt_length,
            max_completion_length=max_completion_length,
            num_train_epochs=self.config.training.num_train_epochs,
            max_steps=self.config.training.max_steps,
            save_steps=self.config.training.save_steps,
            max_grad_norm=self.config.training.max_grad_norm,
            report_to=self.config.training.report_to,
            output_dir=os.path.join(self.config.training.output_dir, self.run_id),
        )
    
    def train(self) -> RunHandle:
        """Execute the training run"""
        try:
            logger.info(f"Starting training run: {self.run_id}")
            
            # Setup environment
            self.setup()
            
            # Create reward functions
            reward_functions = self.create_reward_functions()
            if not reward_functions:
                raise ValueError("No valid reward functions configured")
            
            # Create training arguments
            training_args = self.create_training_args()
            
            # Initialize GRPO trainer
            self.trainer = GRPOTrainer(
                model=self.model,
                processing_class=self.tokenizer,
                reward_funcs=reward_functions,
                args=training_args,
                train_dataset=self.dataset,
            )
            
            # Start training
            logger.info("Starting GRPO training...")
            train_result = self.trainer.train()
            
            # Create run handle with results
            run_handle = RunHandle(
                run_id=self.run_id,
                status="completed",
                created_at=datetime.utcnow().isoformat(),
                config=self.config,
                metrics={
                    "train_loss": train_result.training_loss,
                    "train_runtime": train_result.metrics.get("train_runtime", 0),
                    "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
                },
                artifacts={
                    "model_path": training_args.output_dir,
                    "lora_adapters": os.path.join(training_args.output_dir, "adapter_model"),
                }
            )
            
            logger.info(f"Training completed successfully: {self.run_id}")
            return run_handle
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return RunHandle(
                run_id=self.run_id,
                status="failed",
                created_at=datetime.utcnow().isoformat(),
                config=self.config,
                logs=[f"Error: {str(e)}"]
            )
    
    def save_model(self, output_path: str, merge_lora: bool = False) -> str:
        """Save the trained model"""
        if self.model is None:
            raise ValueError("Model not loaded. Call train() first.")
        
        logger.info(f"Saving model to: {output_path}")
        
        if merge_lora:
            # Save merged model (full weights)
            self.model.save_pretrained_merged(output_path, self.tokenizer)
        else:
            # Save LoRA adapters only
            self.model.save_pretrained(output_path)
            self.tokenizer.save_pretrained(output_path)
        
        logger.info(f"Model saved successfully to: {output_path}")
        return output_path
    
    def save_gguf(self, output_path: str, quantization_type: str = "Q8_0") -> str:
        """Save model in GGUF format for llama.cpp"""
        if self.model is None:
            raise ValueError("Model not loaded. Call train() first.")
        
        logger.info(f"Saving GGUF model to: {output_path}")
        
        self.model.save_pretrained_gguf(
            output_path,
            quantization_type=quantization_type
        )
        
        logger.info(f"GGUF model saved successfully to: {output_path}")
        return output_path
    
    def push_to_hub(self, repo_id: str, token: str, merge_lora: bool = False) -> str:
        """Push model to Hugging Face Hub"""
        if self.model is None:
            raise ValueError("Model not loaded. Call train() first.")
        
        logger.info(f"Pushing model to Hub: {repo_id}")
        
        if merge_lora:
            self.model.push_to_hub_merged(repo_id, self.tokenizer, token=token)
        else:
            self.model.push_to_hub(repo_id, token=token)
            self.tokenizer.push_to_hub(repo_id, token=token)
        
        logger.info(f"Model pushed successfully to: {repo_id}")
        return repo_id


def run_grpo(
    model_id: str,
    dataset_uri: str,
    cfg: Optional[TrainConfig] = None,
    **kwargs
) -> RunHandle:
    """
    Main entry point for running GRPO training.
    
    This function abstracts the four Unsloth GRPO notebooks into a single,
    unified interface.
    
    Args:
        model_id: Hugging Face model ID
        dataset_uri: Dataset URI (HF dataset, S3, local file)
        cfg: Complete training configuration
        **kwargs: Additional configuration parameters
    
    Returns:
        RunHandle: Training run results and metadata
    """
    # Create default configuration if not provided
    if cfg is None:
        from .utils import create_default_config
        cfg = create_default_config(model_id, dataset_uri, **kwargs)
    
    # Validate configuration
    from .utils import validate_config
    validate_config(cfg)
    
    # Create and run trainer
    trainer = UnslothTrainer(cfg)
    return trainer.train()


# Convenience functions for different model types
def run_gemma_grpo(
    model_size: str = "1b",
    dataset_uri: str = "openai/gsm8k",
    **kwargs
) -> RunHandle:
    """Run GRPO training with Gemma model"""
    model_id = f"unsloth/gemma-3-{model_size}-it"
    return run_grpo(model_id, dataset_uri, **kwargs)


def run_llama_grpo(
    model_size: str = "3b",
    dataset_uri: str = "openai/gsm8k",
    **kwargs
) -> RunHandle:
    """Run GRPO training with Llama model"""
    model_id = f"unsloth/Llama-3.2-{model_size}-Instruct"
    return run_grpo(model_id, dataset_uri, **kwargs)


def run_qwen_grpo(
    model_size: str = "4b",
    dataset_uri: str = "openai/gsm8k",
    **kwargs
) -> RunHandle:
    """Run GRPO training with Qwen model"""
    model_id = f"unsloth/qwen2.5-{model_size}-instruct"
    return run_grpo(model_id, dataset_uri, **kwargs)