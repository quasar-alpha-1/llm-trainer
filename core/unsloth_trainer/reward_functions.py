"""
Reward functions for GRPO training.

This module provides the reward functions used in the Unsloth GRPO notebooks,
abstracted into reusable components.
"""

import re
from typing import List, Dict, Any, Callable
from .models import DatasetConfig, RewardFunctionType


def create_format_match_reward(dataset_config: DatasetConfig) -> Callable:
    """
    Create a reward function that rewards exact format matching.
    
    Based on the format matching logic from the notebooks.
    """
    reasoning_start = dataset_config.reasoning_start
    reasoning_end = dataset_config.reasoning_end
    solution_start = dataset_config.solution_start
    solution_end = dataset_config.solution_end
    
    # Create regex pattern for exact format matching
    match_format = re.compile(
        rf"^[\s]{{0,}}"\
        rf"{re.escape(reasoning_start)}.+?{re.escape(reasoning_end)}.*?"\
        rf"{re.escape(solution_start)}(.+?){re.escape(solution_end)}"\
        rf"[\s]{{0,}}$",
        flags = re.MULTILINE | re.DOTALL
    )
    
    def format_match_exactly(completions, **kwargs):
        """Reward exact format matching with 3 points"""
        scores = []
        for completion in completions:
            score = 0
            response = completion[0]["content"]
            # Match if format is seen exactly!
            if match_format.search(response) is not None:
                score += 3.0
            scores.append(score)
        return scores
    
    return format_match_exactly


def create_format_approximate_reward(dataset_config: DatasetConfig) -> Callable:
    """
    Create a reward function that rewards partial format matching.
    
    Based on the approximate format matching logic from the notebooks.
    """
    reasoning_start = dataset_config.reasoning_start
    reasoning_end = dataset_config.reasoning_end
    solution_start = dataset_config.solution_start
    solution_end = dataset_config.solution_end
    
    def format_match_approximately(completions, **kwargs):
        """Reward partial format matching"""
        scores = []
        for completion in completions:
            score = 0
            response = completion[0]["content"]
            # Count how many keywords are seen - we penalize if too many!
            # If we see 1, then plus some points!
            score += 0.5 if response.count(reasoning_start) == 1 else -0.5
            score += 0.5 if response.count(reasoning_end) == 1 else -0.5
            score += 0.5 if response.count(solution_start) == 1 else -0.5
            score += 0.5 if response.count(solution_end) == 1 else -0.5
            scores.append(score)
        return scores
    
    return format_match_approximately


def create_answer_check_reward(dataset_config: DatasetConfig) -> Callable:
    """
    Create a reward function that checks answer correctness.
    
    Based on the answer checking logic from the notebooks.
    """
    reasoning_start = dataset_config.reasoning_start
    reasoning_end = dataset_config.reasoning_end
    solution_start = dataset_config.solution_start
    solution_end = dataset_config.solution_end
    
    # Create regex pattern for extracting answers
    match_format = re.compile(
        rf"^[\s]{{0,}}"\
        rf"{re.escape(reasoning_start)}.+?{re.escape(reasoning_end)}.*?"\
        rf"{re.escape(solution_start)}(.+?){re.escape(solution_end)}"\
        rf"[\s]{{0,}}$",
        flags = re.MULTILINE | re.DOTALL
    )
    
    def check_answer(prompts, completions, answer, **kwargs):
        """Check answer correctness with ratio-based rewards"""
        question = prompts[0][-1]["content"]
        responses = [completion[0]["content"] for completion in completions]

        extracted_responses = [
            guess.group(1)
            if (guess := match_format.search(r)) is not None else None \
            for r in responses
        ]

        scores = []
        for guess, true_answer in zip(extracted_responses, answer):
            score = 0
            if guess is None:
                scores.append(score)
                continue
            
            # Clean up the extracted answer
            guess = guess.strip()
            true_answer = true_answer.strip()
            
            # Exact match gets highest reward
            if guess == true_answer:
                score += 3.0
            # Match if spaces are seen
            elif guess.strip() == true_answer.strip():
                score += 1.5
            else:
                # We also reward it if the answer is close via ratios!
                # Ie if the answer is within some range, reward it!
                try:
                    ratio = float(guess) / float(true_answer)
                    if ratio >= 0.9 and ratio <= 1.1:
                        score += 0.5
                    elif ratio >= 0.8 and ratio <= 1.2:
                        score += 0.25
                    else:
                        score -= 1.0  # Penalize wrong answers
                except:
                    score -= 0.5  # Penalize parsing errors
            scores.append(score)
        return scores
    
    return check_answer


def create_number_check_reward(dataset_config: DatasetConfig) -> Callable:
    """
    Create a reward function that checks numerical answers.
    
    Based on the number checking logic from the notebooks.
    """
    solution_start = dataset_config.solution_start
    
    # Create regex pattern for extracting numbers
    match_numbers = re.compile(
        rf"{re.escape(solution_start)}.*?([\d\.]{{1,}})",
        flags = re.MULTILINE | re.DOTALL
    )
    
    def check_numbers(prompts, completions, answer, **kwargs):
        """Check numerical answer correctness"""
        question = prompts[0][-1]["content"]
        responses = [completion[0]["content"] for completion in completions]

        extracted_responses = [
            guess.group(1)
            if (guess := match_numbers.search(r)) is not None else None \
            for r in responses
        ]

        scores = []
        for guess, true_answer in zip(extracted_responses, answer):
            if guess is None:
                scores.append(0)
                continue
            # Convert to numbers
            try:
                true_answer = float(true_answer.strip())
                guess = float(guess.strip())
                scores.append(1.5 if guess == true_answer else 0.0)
            except:
                scores.append(0)
                continue
        return scores
    
    return check_numbers


def create_custom_reward(custom_code: str) -> Callable:
    """
    Create a custom reward function from code.
    
    WARNING: This executes arbitrary code and should be used with caution.
    In production, this should be sandboxed.
    """
    # TODO: Implement safe execution environment
    raise NotImplementedError("Custom reward functions not yet implemented")


def get_reward_functions(
    reward_type: RewardFunctionType,
    dataset_config: DatasetConfig,
    parameters: Dict[str, Any] = None
) -> Callable:
    """
    Get a reward function based on type and configuration.
    
    Args:
        reward_type: Type of reward function to create
        dataset_config: Dataset configuration for format tokens
        parameters: Additional parameters for the reward function
    
    Returns:
        Callable: Reward function
    """
    if parameters is None:
        parameters = {}
    
    if reward_type == RewardFunctionType.FORMAT_MATCH:
        return create_format_match_reward(dataset_config)
    
    elif reward_type == RewardFunctionType.FORMAT_APPROXIMATE:
        return create_format_approximate_reward(dataset_config)
    
    elif reward_type == RewardFunctionType.ANSWER_CHECK:
        return create_answer_check_reward(dataset_config)
    
    elif reward_type == RewardFunctionType.NUMBER_CHECK:
        return create_number_check_reward(dataset_config)
    
    elif reward_type == RewardFunctionType.CUSTOM:
        custom_code = parameters.get("custom_code")
        if custom_code:
            return create_custom_reward(custom_code)
        else:
            raise ValueError("Custom reward function requires 'custom_code' parameter")
    
    else:
        raise ValueError(f"Unknown reward function type: {reward_type}")


# Predefined reward function combinations
def get_gsm8k_rewards(dataset_config: DatasetConfig) -> List[Callable]:
    """Get the standard reward functions used for GSM8K dataset"""
    return [
        create_format_match_reward(dataset_config),
        create_format_approximate_reward(dataset_config),
        create_answer_check_reward(dataset_config),
        create_number_check_reward(dataset_config),
    ]


def get_math_rewards(dataset_config: DatasetConfig) -> List[Callable]:
    """Get reward functions optimized for mathematical reasoning"""
    return [
        create_format_match_reward(dataset_config),
        create_number_check_reward(dataset_config),
    ]


def get_general_rewards(dataset_config: DatasetConfig) -> List[Callable]:
    """Get general-purpose reward functions"""
    return [
        create_format_match_reward(dataset_config),
        create_format_approximate_reward(dataset_config),
    ]