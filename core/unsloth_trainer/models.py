"""
Data models for the Unsloth Trainer system.

Defines the configuration structures for models, datasets, and training parameters.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class ModelType(str, Enum):
    """Supported model types"""
    GEMMA_3_1B = "unsloth/gemma-3-1b-it"
    GEMMA_3_4B = "unsloth/gemma-3-4b-it"
    GEMMA_3_12B = "unsloth/gemma-3-12b-it"
    GEMMA_3_27B = "unsloth/gemma-3-27b-it"
    LLAMA_3_1_8B = "unsloth/Llama-3.1-8B"
    LLAMA_3_2_3B = "unsloth/Llama-3.2-3B"
    LLAMA_3_3_70B = "unsloth/Llama-3.3-70B"
    MISTRAL_7B = "unsloth/mistral-7b-instruct-v0.3"
    PHI_4 = "unsloth/Phi-4"
    QWEN_3_4B = "unsloth/qwen2.5-4b-instruct"
    DEEPSEEK_R1 = "unsloth/deepseek-r1-0528-qwen2.5-8b"


class QuantizationType(str, Enum):
    """Model quantization options"""
    NONE = "none"
    FOUR_BIT = "4bit"
    EIGHT_BIT = "8bit"


class RewardFunctionType(str, Enum):
    """Available reward function types"""
    FORMAT_MATCH = "format_match"
    FORMAT_APPROXIMATE = "format_approximate"
    ANSWER_CHECK = "answer_check"
    NUMBER_CHECK = "number_check"
    CUSTOM = "custom"


class ModelConfig(BaseModel):
    """Configuration for model loading and setup"""
    model_id: str = Field(..., description="Hugging Face model ID")
    max_seq_length: int = Field(1024, ge=512, le=8192, description="Maximum sequence length")
    load_in_4bit: bool = Field(False, description="Use 4-bit quantization")
    load_in_8bit: bool = Field(False, description="Use 8-bit quantization")
    full_finetuning: bool = Field(False, description="Full model fine-tuning")
    fast_inference: bool = Field(True, description="Enable vLLM fast inference")
    gpu_memory_utilization: float = Field(0.6, ge=0.1, le=1.0, description="GPU memory utilization")
    token: Optional[str] = Field(None, description="Hugging Face token for gated models")

    @validator('model_id')
    def validate_model_id(cls, v):
        """Validate model ID format"""
        if not v or '/' not in v:
            raise ValueError("Model ID must be in format 'org/model-name'")
        return v

    @validator('load_in_4bit', 'load_in_8bit')
    def validate_quantization(cls, v, values):
        """Ensure only one quantization method is selected"""
        if values.get('load_in_4bit') and values.get('load_in_8bit'):
            raise ValueError("Cannot use both 4-bit and 8-bit quantization")
        return v


class LoRAConfig(BaseModel):
    """LoRA adapter configuration"""
    r: int = Field(8, ge=1, le=256, description="LoRA rank")
    lora_alpha: int = Field(8, ge=1, le=256, description="LoRA alpha parameter")
    lora_dropout: float = Field(0.0, ge=0.0, le=1.0, description="LoRA dropout")
    bias: str = Field("none", description="Bias type")
    target_modules: Optional[List[str]] = Field(None, description="Target modules for LoRA")
    finetune_vision_layers: bool = Field(False, description="Fine-tune vision layers")
    finetune_language_layers: bool = Field(True, description="Fine-tune language layers")
    finetune_attention_modules: bool = Field(True, description="Fine-tune attention modules")
    finetune_mlp_modules: bool = Field(True, description="Fine-tune MLP modules")
    use_gradient_checkpointing: str = Field("unsloth", description="Gradient checkpointing method")


class DatasetConfig(BaseModel):
    """Dataset configuration"""
    dataset_uri: str = Field(..., description="Dataset URI (HF dataset, S3, local file)")
    dataset_type: str = Field("huggingface", description="Dataset type (huggingface, csv, json, parquet)")
    split: str = Field("train", description="Dataset split to use")
    max_samples: Optional[int] = Field(None, ge=1, description="Maximum number of samples")
    system_prompt: Optional[str] = Field(None, description="System prompt template")
    user_prompt_column: str = Field("question", description="Column containing user prompts")
    answer_column: str = Field("answer", description="Column containing answers")
    reasoning_start: str = Field("<start_working_out>", description="Reasoning start token")
    reasoning_end: str = Field("<end_working_out>", description="Reasoning end token")
    solution_start: str = Field("<SOLUTION>", description="Solution start token")
    solution_end: str = Field("</SOLUTION>", description="Solution end token")

    @validator('dataset_uri')
    def validate_dataset_uri(cls, v):
        """Validate dataset URI format"""
        if not v:
            raise ValueError("Dataset URI cannot be empty")
        return v


class RewardConfig(BaseModel):
    """Reward function configuration"""
    reward_type: RewardFunctionType = Field(..., description="Type of reward function")
    weight: float = Field(1.0, ge=0.0, description="Weight for this reward function")
    custom_code: Optional[str] = Field(None, description="Custom reward function code")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class TrainingConfig(BaseModel):
    """Training configuration"""
    learning_rate: float = Field(5e-6, ge=1e-8, le=1e-3, description="Learning rate")
    adam_beta1: float = Field(0.9, ge=0.0, le=1.0, description="Adam beta1")
    adam_beta2: float = Field(0.99, ge=0.0, le=1.0, description="Adam beta2")
    weight_decay: float = Field(0.1, ge=0.0, le=1.0, description="Weight decay")
    warmup_ratio: float = Field(0.1, ge=0.0, le=1.0, description="Warmup ratio")
    lr_scheduler_type: str = Field("cosine", description="Learning rate scheduler type")
    optim: str = Field("adamw_torch_fused", description="Optimizer")
    logging_steps: int = Field(1, ge=1, description="Logging frequency")
    per_device_train_batch_size: int = Field(1, ge=1, description="Batch size per device")
    gradient_accumulation_steps: int = Field(1, ge=1, description="Gradient accumulation steps")
    num_generations: int = Field(4, ge=1, le=16, description="Number of generations per step")
    max_prompt_length: int = Field(256, ge=64, description="Maximum prompt length")
    max_completion_length: Optional[int] = Field(None, description="Maximum completion length")
    num_train_epochs: Optional[int] = Field(None, ge=1, description="Number of training epochs")
    max_steps: Optional[int] = Field(None, ge=1, description="Maximum training steps")
    save_steps: int = Field(50, ge=1, description="Save frequency")
    max_grad_norm: float = Field(0.1, ge=0.0, description="Maximum gradient norm")
    report_to: str = Field("none", description="Reporting backend")
    output_dir: str = Field("outputs", description="Output directory")


class TrainConfig(BaseModel):
    """Complete training configuration"""
    model: ModelConfig = Field(..., description="Model configuration")
    lora: LoRAConfig = Field(..., description="LoRA configuration")
    dataset: DatasetConfig = Field(..., description="Dataset configuration")
    rewards: List[RewardConfig] = Field(..., description="Reward functions")
    training: TrainingConfig = Field(..., description="Training configuration")
    random_state: int = Field(3407, description="Random seed")
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        validate_assignment = True


class RunHandle(BaseModel):
    """Handle for tracking training runs"""
    run_id: str = Field(..., description="Unique run identifier")
    status: str = Field("pending", description="Run status")
    created_at: str = Field(..., description="Creation timestamp")
    config: TrainConfig = Field(..., description="Training configuration")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Training metrics")
    logs: Optional[List[str]] = Field(None, description="Training logs")
    artifacts: Optional[Dict[str, str]] = Field(None, description="Output artifacts")