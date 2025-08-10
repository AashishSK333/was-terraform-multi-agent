"""
Gemini agent for image parsing (Step 1)
"""

import base64
from typing import Dict, Any, Optional
import google.generativeai as genai
from PIL import Image
import io

from .base_agent import BaseAgent, AgentResponse


class GeminiAgent(BaseAgent):
    """Gemini agent specialized for architecture image parsing"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        super().__init__("Gemini Vision Agent", model, api_key)
        
    async def initialize(self):
        """Initialize Gemini client"""
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
        
    async def process(self, input_data: Any, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Parse architecture image to extract components and relationships
        
        Args:
            input_data: Image file path or base64 encoded image
            context: Additional context for processing
            
        Returns:
            AgentResponse with parsed architecture details
        """
        try:
            # Load and process image
            if isinstance(input_data, str):
                if input_data.startswith('data:image'):
                    # Base64 encoded image
                    image_data = input_data.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                else:
                    # File path
                    image = Image.open(input_data)
            else:
                image = input_data
                
            # Prepare prompt for architecture parsing
            prompt = """
            You are an expert AWS architecture analyst. Analyze this architecture diagram and provide a detailed breakdown:

            1. **Components Identified**: List all AWS services, components, and resources shown in the diagram.
            2. **Relationships**: Describe how components are connected and interact with each other.
            3. **Data Flow**: Explain the data flow and communication patterns.
            4. **Network Architecture**: Identify VPCs, subnets, security groups, and networking components.
            5. **Storage & Database**: Identify storage solutions, databases, and data persistence layers.
            6. **Compute Resources**: List EC2 instances, Lambda functions, containers, or other compute resources.
            7. **Security Components**: Identify security groups, IAM roles, encryption, and access controls.
            8. **Scalability & High Availability**: Note load balancers, auto-scaling groups, multi-AZ deployments.

            If the diagram contains any sequences (such as arrows, numbered steps, or ordered flows) between interfaces or services, use these sequences to better understand the context and accurately interpret the interactions and workflow.

            Provide the response in JSON format with clear categorization of components and their properties.
            Include confidence levels for each identified component (0-100%).
            """
            
            # Generate response
            response = await self.client.generate_content_async([prompt, image])
            
            return AgentResponse(
                content=response.text,
                confidence=0.95,  # High confidence for Gemini vision capabilities
                metadata={
                    "agent": self.name,
                    "model": self.model,
                    "task": "architecture_image_parsing",
                    "input_type": "image"
                }
            )
            
        except Exception as e:
            return AgentResponse(
                content="",
                success=False,
                error_message=f"Gemini processing error: {str(e)}"
            )
