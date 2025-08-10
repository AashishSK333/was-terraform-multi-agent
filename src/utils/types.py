"""
Type definitions for the multi-agent orchestration system
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional

from ..agents.base_agent import AgentResponse


class ProcessStep(Enum):
    """Enumeration of process steps"""
    IMAGE_PARSING = 1
    MODEL_EVALUATION_1 = 2
    TERRAFORM_CREATION = 3
    MODEL_EVALUATION_2 = 4


@dataclass
class StepResult:
    """Result of a single step in the process"""
    step: ProcessStep
    response: AgentResponse
    score: Optional[float] = None
    passed_threshold: bool = False
    retry_count: int = 0
    execution_time: float = 0.0


@dataclass
class OrchestrationConfig:
    """Configuration for the orchestration system"""
    evaluation_threshold: float = 80.0
    max_retries: int = 3
    enable_parallel_execution: bool = True
    timeout_seconds: int = 300
    
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    
    # Model specifications
    gemini_model: str = "gemini-1.5-pro"
    gpt4_model: str = "gpt-4o"
    claude_model: str = "claude-3-5-sonnet-20241022"