"""
Fixed GPT-4o agent for evaluation tasks (Steps 2 and 4)
"""

import json
import re
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

from .base_agent import BaseAgent, AgentResponse


class GPT4oAgent(BaseAgent):
    """GPT-4o agent specialized for evaluation and scoring"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        super().__init__("GPT-4o Evaluation Agent", model, api_key)
        
    async def initialize(self):
        """Initialize OpenAI client"""
        self.client = AsyncOpenAI(api_key=self.api_key)

    def _extract_json_from_response(self, response_content: str) -> dict:
        """Extract JSON from response content, handling markdown code blocks"""
        try:
            # First, try to parse as direct JSON
            return json.loads(response_content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            match = re.search(json_pattern, response_content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Try to find JSON object in the text
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, response_content, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
            
            # If all else fails, look for score values
            score_pattern = r'"overall_score"\s*:\s*(\d+)'
            score_match = re.search(score_pattern, response_content)
            if score_match:
                return {"overall_score": int(score_match.group(1))}
            
            return {}

    async def evaluate_parsing_response(self, original_input: Any, parsing_response: str) -> AgentResponse:
        """
        Evaluate the quality of image parsing response (Step 2)
        """
        prompt = f"""
        You are an expert evaluator for AWS architecture analysis. Evaluate the following image parsing response:

        PARSING RESPONSE TO EVALUATE:
        {parsing_response}

        EVALUATION CRITERIA (Score each out of 20 points, total 100):
        1. **Completeness** (20 points): Are all visible components identified?
        2. **Accuracy** (20 points): Are the identified components correctly named and categorized?
        3. **Relationships** (20 points): Are component relationships and connections properly described?
        4. **Technical Detail** (20 points): Is sufficient technical detail provided for Terraform generation?
        5. **Structure** (20 points): Is the response well-structured and parseable?

        Provide your evaluation in the following JSON format:
        {{
            "overall_score": <0-100>,
            "criteria_scores": {{
                "completeness": <0-20>,
                "accuracy": <0-20>,
                "relationships": <0-20>,
                "technical_detail": <0-20>,
                "structure": <0-20>
            }},
            "strengths": ["list of strengths"],
            "weaknesses": ["list of weaknesses"],
            "recommendations": ["list of improvement recommendations"],
            "pass_threshold": <true/false for score >= 80>
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AWS architecture evaluator. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            evaluation_result = response.choices[0].message.content
            
            # Extract score using improved JSON parsing
            eval_data = self._extract_json_from_response(evaluation_result)
            score = eval_data.get("overall_score", 0)
            
            # Ensure score is an integer
            if isinstance(score, str):
                score = int(score) if score.isdigit() else 0
            
            print(f"🔍 Debug: Extracted score = {score} from evaluation")
            
            return AgentResponse(
                content=evaluation_result,
                confidence=score / 100.0,
                metadata={
                    "agent": self.name,
                    "model": self.model,
                    "task": "parsing_evaluation",
                    "score": score,
                    "threshold_passed": score >= 80
                }
            )
            
        except Exception as e:
            print(f"❌ GPT-4o evaluation error: {str(e)}")
            return AgentResponse(
                content="",
                success=False,
                error_message=f"GPT-4o evaluation error: {str(e)}"
            )

    async def evaluate_terraform_response(self, requirements: str, terraform_code: str) -> AgentResponse:
        """
        Evaluate the quality of generated Terraform code (Step 4)
        """
        prompt = f"""
        You are an expert Terraform and AWS architecture evaluator. Evaluate the following Terraform code against the requirements:

        ORIGINAL REQUIREMENTS:
        {requirements}

        TERRAFORM CODE TO EVALUATE:
        {terraform_code}

        EVALUATION CRITERIA (Score each out of 20 points, total 100):
        1. **Requirements Compliance** (20 points): Does the code fulfill all specified requirements?
        2. **Best Practices** (20 points): Does the code follow Terraform and AWS best practices?
        3. **Security** (20 points): Are security best practices implemented?
        4. **Completeness** (20 points): Are all necessary resources and configurations included?
        5. **Code Quality** (20 points): Is the code well-structured, readable, and maintainable?

        Provide your evaluation in the following JSON format:
        {{
            "overall_score": <0-100>,
            "criteria_scores": {{
                "requirements_compliance": <0-20>,
                "best_practices": <0-20>,
                "security": <0-20>,
                "completeness": <0-20>,
                "code_quality": <0-20>
            }},
            "strengths": ["list of strengths"],
            "weaknesses": ["list of weaknesses"],
            "security_concerns": ["list of security issues if any"],
            "recommendations": ["list of improvement recommendations"],
            "pass_threshold": <true/false for score >= 80>
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Terraform and AWS evaluator. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            evaluation_result = response.choices[0].message.content
            
            # Extract score using improved JSON parsing
            eval_data = self._extract_json_from_response(evaluation_result)
            score = eval_data.get("overall_score", 0)
            
            # Ensure score is an integer
            if isinstance(score, str):
                score = int(score) if score.isdigit() else 0
                
            print(f"🔍 Debug: Extracted score = {score} from terraform evaluation")
            
            return AgentResponse(
                content=evaluation_result,
                confidence=score / 100.0,
                metadata={
                    "agent": self.name,
                    "model": self.model,
                    "task": "terraform_evaluation",
                    "score": score,
                    "threshold_passed": score >= 80
                }
            )
            
        except Exception as e:
            print(f"❌ GPT-4o terraform evaluation error: {str(e)}")
            return AgentResponse(
                content="",
                success=False,
                error_message=f"GPT-4o evaluation error: {str(e)}"
            )

    async def process(self, input_data: Any, context: Dict[str, Any] = None) -> AgentResponse:
        """
        General process method that routes to specific evaluation methods
        """
        if context and context.get("task") == "parsing_evaluation":
            return await self.evaluate_parsing_response(
                context.get("original_input"), 
                input_data
            )
        elif context and context.get("task") == "terraform_evaluation":
            return await self.evaluate_terraform_response(
                context.get("requirements"), 
                input_data
            )
        else:
            return AgentResponse(
                content="",
                success=False,
                error_message="Invalid task specified for GPT-4o agent"
            )
