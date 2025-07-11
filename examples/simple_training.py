#!/usr/bin/env python3
"""
Simple example of using the Unsloth Trainer system.

This script demonstrates how to use the abstracted training interface
to run GRPO training with minimal configuration.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.unsloth_trainer import run_grpo, run_gemma_grpo, run_llama_grpo, run_qwen_grpo
from core.unsloth_trainer.models import TrainConfig, ModelConfig, LoRAConfig, DatasetConfig, TrainingConfig, RewardConfig, RewardFunctionType
from core.unsloth_trainer.utils import format_config_summary


def example_simple_training():
    """Example of simple training with default configuration"""
    print("🚀 Starting simple GRPO training example...")
    
    # Simple training with default configuration
    result = run_gemma_grpo(
        model_size="1b",
        dataset_uri="openai/gsm8k",
        max_steps=10,  # Small number for demo
        max_samples=100  # Small dataset for demo
    )
    
    print(f"✅ Training completed!")
    print(f"Run ID: {result.run_id}")
    print(f"Status: {result.status}")
    print(f"Metrics: {result.metrics}")
    
    return result


def example_custom_configuration():
    """Example of training with custom configuration"""
    print("\n🔧 Starting custom configuration example...")
    
    # Create custom configuration
    config = TrainConfig(
        model=ModelConfig(
            model_id="unsloth/gemma-3-1b-it",
            max_seq_length=1024,
            load_in_4bit=False,
        ),
        lora=LoRAConfig(
            r=16,  # Higher rank for better performance
            lora_alpha=16,
        ),
        dataset=DatasetConfig(
            dataset_uri="openai/gsm8k",
            dataset_type="huggingface",
            max_samples=200,
        ),
        rewards=[
            RewardConfig(
                reward_type=RewardFunctionType.FORMAT_MATCH,
                weight=1.0
            ),
            RewardConfig(
                reward_type=RewardFunctionType.ANSWER_CHECK,
                weight=2.0
            ),
        ],
        training=TrainingConfig(
            learning_rate=1e-5,
            max_steps=20,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=2,
        ),
    )
    
    # Print configuration summary
    print(format_config_summary(config))
    
    # Run training with custom config
    result = run_grpo(
        model_id="unsloth/gemma-3-1b-it",
        dataset_uri="openai/gsm8k",
        cfg=config
    )
    
    print(f"✅ Custom training completed!")
    print(f"Run ID: {result.run_id}")
    print(f"Status: {result.status}")
    
    return result


def example_different_models():
    """Example of training with different model types"""
    print("\n🤖 Starting different models example...")
    
    models = [
        ("gemma", "1b"),
        ("llama", "3b"),
        ("qwen", "4b"),
    ]
    
    results = []
    
    for model_family, size in models:
        print(f"\nTraining {model_family.upper()} {size} model...")
        
        try:
            if model_family == "gemma":
                result = run_gemma_grpo(
                    model_size=size,
                    dataset_uri="openai/gsm8k",
                    max_steps=5,
                    max_samples=50
                )
            elif model_family == "llama":
                result = run_llama_grpo(
                    model_size=size,
                    dataset_uri="openai/gsm8k",
                    max_steps=5,
                    max_samples=50
                )
            elif model_family == "qwen":
                result = run_qwen_grpo(
                    model_size=size,
                    dataset_uri="openai/gsm8k",
                    max_steps=5,
                    max_samples=50
                )
            
            results.append((model_family, size, result))
            print(f"✅ {model_family.upper()} {size} training completed!")
            
        except Exception as e:
            print(f"❌ {model_family.upper()} {size} training failed: {str(e)}")
            results.append((model_family, size, None))
    
    return results


def main():
    """Main function to run examples"""
    print("🎯 Unsloth Trainer Examples")
    print("=" * 50)
    
    # Check if CUDA is available
    import torch
    if not torch.cuda.is_available():
        print("⚠️  CUDA not available. Training will be slow on CPU.")
        print("   Consider using a GPU for better performance.")
    
    try:
        # Example 1: Simple training
        result1 = example_simple_training()
        
        # Example 2: Custom configuration
        result2 = example_custom_configuration()
        
        # Example 3: Different models
        results3 = example_different_models()
        
        print("\n🎉 All examples completed!")
        print("\nSummary:")
        print(f"- Simple training: {result1.status}")
        print(f"- Custom training: {result2.status}")
        print("- Model comparisons:")
        for model_family, size, result in results3:
            status = result.status if result else "failed"
            print(f"  - {model_family.upper()} {size}: {status}")
        
    except Exception as e:
        print(f"❌ Example failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()