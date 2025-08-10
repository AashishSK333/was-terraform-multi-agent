"""
Base agent class for all LLM agents in the system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential


class AgentResponse(BaseModel):
    """Standard response format for all agents"""
    content: str
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = {}
    success: bool = True
    error_message: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all LLM agents"""
    
    def __init__(self, name: str, model: str, api_key: str):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.client = None
        
    @abstractmethod
    async def initialize(self):
        """Initialize the agent's client"""
        pass
    
    @abstractmethod
    async def process(self, input_data: Any, context: Dict[str, Any] = None) -> AgentResponse:
        """Process input and return response"""
        pass
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def safe_process(self, input_data: Any, context: Dict[str, Any] = None) -> AgentResponse:
        """Process with retry logic"""
        try:
            return await self.process(input_data, context)
        except Exception as e:
            return AgentResponse(
                content="",
                success=False,
                error_message=str(e)
            )
    
    def __str__(self):
        return f"{self.name} ({self.model})"
