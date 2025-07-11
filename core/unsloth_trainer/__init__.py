"""
Unsloth Trainer - Core training logic abstraction

This package abstracts the four Unsloth GRPO notebooks into a reusable,
production-grade training system.
"""

from .trainer import run_grpo, TrainConfig, RunHandle
from .models import ModelConfig, DatasetConfig, RewardConfig
from .utils import get_available_models, validate_config

__version__ = "0.1.0"
__all__ = [
    "run_grpo",
    "TrainConfig", 
    "RunHandle",
    "ModelConfig",
    "DatasetConfig", 
    "RewardConfig",
    "get_available_models",
    "validate_config"
]