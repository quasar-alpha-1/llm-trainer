"""
Data processing module for handling datasets.

This module provides functionality for loading and preprocessing datasets
from various sources (Hugging Face, S3, local files) and formatting them
for GRPO training.
"""

import re
import logging
from typing import Optional, Dict, Any
from datasets import load_dataset, Dataset
from transformers import PreTrainedTokenizer

from .models import DatasetConfig

logger = logging.getLogger(__name__)


def extract_hash_answer(text: str) -> Optional[str]:
    """
    Extract answer from text that contains #### separator.
    
    Based on the GSM8K answer extraction logic from the notebooks.
    """
    if "####" not in text:
        return None
    return text.split("####")[1].strip()


def create_system_prompt(dataset_config: DatasetConfig) -> str:
    """
    Create system prompt based on dataset configuration.
    
    Based on the system prompt creation logic from the notebooks.
    """
    reasoning_start = dataset_config.reasoning_start
    reasoning_end = dataset_config.reasoning_end
    solution_start = dataset_config.solution_start
    solution_end = dataset_config.solution_end
    
    return f"""You are given a problem.
Think about the problem and provide your working out.
Place it between {reasoning_start} and {reasoning_end}.
Then, provide your solution between {solution_start}{solution_end}"""


def load_huggingface_dataset(dataset_uri: str, split: str = "train", max_samples: Optional[int] = None) -> Dataset:
    """
    Load dataset from Hugging Face Hub.
    
    Args:
        dataset_uri: Hugging Face dataset ID
        split: Dataset split to load
        max_samples: Maximum number of samples to load
    
    Returns:
        Dataset: Loaded dataset
    """
    logger.info(f"Loading Hugging Face dataset: {dataset_uri}")
    
    try:
        dataset = load_dataset(dataset_uri, split=split)
        
        if max_samples:
            dataset = dataset.select(range(min(max_samples, len(dataset))))
            logger.info(f"Loaded {len(dataset)} samples from {dataset_uri}")
        
        return dataset
    
    except Exception as e:
        logger.error(f"Failed to load dataset {dataset_uri}: {str(e)}")
        raise


def load_csv_dataset(file_path: str, max_samples: Optional[int] = None) -> Dataset:
    """
    Load dataset from CSV file.
    
    Args:
        file_path: Path to CSV file
        max_samples: Maximum number of samples to load
    
    Returns:
        Dataset: Loaded dataset
    """
    logger.info(f"Loading CSV dataset: {file_path}")
    
    try:
        dataset = load_dataset("csv", data_files=file_path, split="train")
        
        if max_samples:
            dataset = dataset.select(range(min(max_samples, len(dataset))))
            logger.info(f"Loaded {len(dataset)} samples from {file_path}")
        
        return dataset
    
    except Exception as e:
        logger.error(f"Failed to load CSV dataset {file_path}: {str(e)}")
        raise


def load_json_dataset(file_path: str, max_samples: Optional[int] = None) -> Dataset:
    """
    Load dataset from JSON file.
    
    Args:
        file_path: Path to JSON file
        max_samples: Maximum number of samples to load
    
    Returns:
        Dataset: Loaded dataset
    """
    logger.info(f"Loading JSON dataset: {file_path}")
    
    try:
        dataset = load_dataset("json", data_files=file_path, split="train")
        
        if max_samples:
            dataset = dataset.select(range(min(max_samples, len(dataset))))
            logger.info(f"Loaded {len(dataset)} samples from {file_path}")
        
        return dataset
    
    except Exception as e:
        logger.error(f"Failed to load JSON dataset {file_path}: {str(e)}")
        raise


def load_parquet_dataset(file_path: str, max_samples: Optional[int] = None) -> Dataset:
    """
    Load dataset from Parquet file.
    
    Args:
        file_path: Path to Parquet file
        max_samples: Maximum number of samples to load
    
    Returns:
        Dataset: Loaded dataset
    """
    logger.info(f"Loading Parquet dataset: {file_path}")
    
    try:
        dataset = load_dataset("parquet", data_files=file_path, split="train")
        
        if max_samples:
            dataset = dataset.select(range(min(max_samples, len(dataset))))
            logger.info(f"Loaded {len(dataset)} samples from {file_path}")
        
        return dataset
    
    except Exception as e:
        logger.error(f"Failed to load Parquet dataset {file_path}: {str(e)}")
        raise


def load_s3_dataset(s3_uri: str, max_samples: Optional[int] = None) -> Dataset:
    """
    Load dataset from S3.
    
    Args:
        s3_uri: S3 URI (s3://bucket/path/to/file)
        max_samples: Maximum number of samples to load
    
    Returns:
        Dataset: Loaded dataset
    """
    logger.info(f"Loading S3 dataset: {s3_uri}")
    
    try:
        # Determine file type from extension
        if s3_uri.endswith('.csv'):
            dataset = load_dataset("csv", data_files=s3_uri, split="train")
        elif s3_uri.endswith('.json'):
            dataset = load_dataset("json", data_files=s3_uri, split="train")
        elif s3_uri.endswith('.parquet'):
            dataset = load_dataset("parquet", data_files=s3_uri, split="train")
        else:
            raise ValueError(f"Unsupported file type for S3 URI: {s3_uri}")
        
        if max_samples:
            dataset = dataset.select(range(min(max_samples, len(dataset))))
            logger.info(f"Loaded {len(dataset)} samples from {s3_uri}")
        
        return dataset
    
    except Exception as e:
        logger.error(f"Failed to load S3 dataset {s3_uri}: {str(e)}")
        raise


def load_dataset_from_uri(dataset_config: DatasetConfig) -> Dataset:
    """
    Load dataset from various sources based on URI.
    
    Args:
        dataset_config: Dataset configuration
    
    Returns:
        Dataset: Loaded dataset
    """
    dataset_uri = dataset_config.dataset_uri
    dataset_type = dataset_config.dataset_type
    split = dataset_config.split
    max_samples = dataset_config.max_samples
    
    if dataset_type == "huggingface":
        return load_huggingface_dataset(dataset_uri, split, max_samples)
    
    elif dataset_type == "csv":
        return load_csv_dataset(dataset_uri, max_samples)
    
    elif dataset_type == "json":
        return load_json_dataset(dataset_uri, max_samples)
    
    elif dataset_type == "parquet":
        return load_parquet_dataset(dataset_uri, max_samples)
    
    elif dataset_type == "s3":
        return load_s3_dataset(dataset_uri, max_samples)
    
    else:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")


def process_gsm8k_dataset(dataset: Dataset, dataset_config: DatasetConfig) -> Dataset:
    """
    Process GSM8K dataset for GRPO training.
    
    Based on the GSM8K processing logic from the notebooks.
    """
    logger.info("Processing GSM8K dataset")
    
    def process_example(example):
        # Extract answer from GSM8K format
        answer = extract_hash_answer(example[dataset_config.answer_column])
        
        # Create system prompt
        system_prompt = dataset_config.system_prompt or create_system_prompt(dataset_config)
        
        # Format for chat template
        return {
            "prompt": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": example[dataset_config.user_prompt_column]},
            ],
            "answer": answer,
        }
    
    processed_dataset = dataset.map(process_example)
    logger.info(f"Processed {len(processed_dataset)} examples")
    
    return processed_dataset


def process_generic_dataset(dataset: Dataset, dataset_config: DatasetConfig) -> Dataset:
    """
    Process generic dataset for GRPO training.
    
    For datasets that don't follow GSM8K format.
    """
    logger.info("Processing generic dataset")
    
    def process_example(example):
        # Create system prompt
        system_prompt = dataset_config.system_prompt or create_system_prompt(dataset_config)
        
        # Format for chat template
        return {
            "prompt": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": example[dataset_config.user_prompt_column]},
            ],
            "answer": example[dataset_config.answer_column],
        }
    
    processed_dataset = dataset.map(process_example)
    logger.info(f"Processed {len(processed_dataset)} examples")
    
    return processed_dataset


def process_dataset(dataset_config: DatasetConfig, tokenizer: PreTrainedTokenizer) -> Dataset:
    """
    Main function to load and process dataset for GRPO training.
    
    Args:
        dataset_config: Dataset configuration
        tokenizer: Tokenizer for validation
    
    Returns:
        Dataset: Processed dataset ready for training
    """
    logger.info("Starting dataset processing")
    
    # Load dataset
    dataset = load_dataset_from_uri(dataset_config)
    
    # Determine processing method based on dataset
    if dataset_config.dataset_uri.startswith("openai/gsm8k"):
        processed_dataset = process_gsm8k_dataset(dataset, dataset_config)
    else:
        processed_dataset = process_generic_dataset(dataset, dataset_config)
    
    # Validate dataset format
    validate_dataset_format(processed_dataset, tokenizer)
    
    logger.info("Dataset processing completed")
    return processed_dataset


def validate_dataset_format(dataset: Dataset, tokenizer: PreTrainedTokenizer) -> None:
    """
    Validate that dataset has correct format for GRPO training.
    
    Args:
        dataset: Dataset to validate
        tokenizer: Tokenizer for validation
    """
    logger.info("Validating dataset format")
    
    if len(dataset) == 0:
        raise ValueError("Dataset is empty")
    
    # Check first example
    example = dataset[0]
    
    # Validate required fields
    if "prompt" not in example:
        raise ValueError("Dataset missing 'prompt' field")
    
    if "answer" not in example:
        raise ValueError("Dataset missing 'answer' field")
    
    # Validate prompt format
    prompt = example["prompt"]
    if not isinstance(prompt, list):
        raise ValueError("Prompt must be a list of message dictionaries")
    
    if len(prompt) < 2:
        raise ValueError("Prompt must have at least system and user messages")
    
    # Validate message format
    for message in prompt:
        if not isinstance(message, dict):
            raise ValueError("Each message must be a dictionary")
        
        if "role" not in message or "content" not in message:
            raise ValueError("Each message must have 'role' and 'content' fields")
    
    # Test tokenization
    try:
        text = tokenizer.apply_chat_template(
            prompt,
            add_generation_prompt=True,
            tokenize=False
        )
        tokens = tokenizer(text, return_tensors="pt")
        logger.info(f"Sample text tokenized successfully: {tokens.input_ids.shape}")
    except Exception as e:
        raise ValueError(f"Failed to tokenize sample text: {str(e)}")
    
    logger.info("Dataset format validation passed")