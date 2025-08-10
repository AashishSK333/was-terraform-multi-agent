"""
Main orchestrator for the multi-agent system
Coordinates all 4 steps with scoring thresholds
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List

from ..agents.gemini_agent import GeminiAgent
from ..agents.gpt4o_agent import GPT4oAgent
from ..agents.claude_agent import ClaudeAgent
from ..agents.base_agent import AgentResponse
from ..utils.output_logger import OrchestrationLogger
from ..utils.types import ProcessStep, StepResult, OrchestrationConfig


class MultiAgentOrchestrator:
    """Coordinates all steps of the process"""
    
    def __init__(self, config: OrchestrationConfig):
        """Initialize the orchestrator"""
        self.config = config
        self.gemini_agent: Optional[GeminiAgent] = None
        self.gpt4o_agent: Optional[GPT4oAgent] = None
        self.claude_agent: Optional[ClaudeAgent] = None
        self.step_results: List[StepResult] = []
        self.current_context: Dict[str, Any] = {}
        self.logger = OrchestrationLogger()
        
    async def initialize_agents(self):
        """Initialize all agents"""
        print("🔧 Initializing agents...")
        
        # Log configuration
        config_dict = {
            "evaluation_threshold": self.config.evaluation_threshold,
            "max_retries": self.config.max_retries,
            "enable_parallel_execution": self.config.enable_parallel_execution,
            "timeout_seconds": self.config.timeout_seconds,
            "gemini_model": self.config.gemini_model,
            "gpt4_model": self.config.gpt4_model,
            "claude_model": self.config.claude_model
        }
        self.logger.log_configuration(config_dict)
        
        try:
            # Initialize Gemini agent
            self.gemini_agent = GeminiAgent(
                api_key=self.config.google_api_key,
                model=self.config.gemini_model
            )
            await self.gemini_agent.initialize()
            
            # Initialize GPT-4o agent
            self.gpt4o_agent = GPT4oAgent(
                api_key=self.config.openai_api_key,
                model=self.config.gpt4_model
            )
            await self.gpt4o_agent.initialize()
            
            # Initialize Claude agent
            self.claude_agent = ClaudeAgent(
                api_key=self.config.anthropic_api_key,
                model=self.config.claude_model
            )
            await self.claude_agent.initialize()
            
            print("✅ All agents initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize agents: {str(e)}")
            raise
    
    async def execute_step_1_image_parsing(self, image_input: Any) -> StepResult:
        """
        Step 1: Architecture Image Parsing using Gemini
        """
        print("🔄 Starting Step 1: Image Parsing with Gemini")
        self.logger.log_step_start(ProcessStep.IMAGE_PARSING, str(image_input))
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self.gemini_agent.safe_process(image_input)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            result = StepResult(
                step=ProcessStep.IMAGE_PARSING,
                response=response,
                execution_time=execution_time
            )
            
            if response.success:
                self.current_context["parsed_architecture"] = response.content
                self.current_context["original_image"] = image_input
                print("✅ Step 1 completed successfully")
            else:
                print(f"❌ Step 1 failed: {response.error_message}")
            
            self.logger.log_step_completion(result)
            return result
            
        except Exception as e:
            print(f"❌ Step 1 error: {str(e)}")
            result = StepResult(
                step=ProcessStep.IMAGE_PARSING,
                response=AgentResponse(content="", success=False, error_message=str(e)),
                execution_time=asyncio.get_event_loop().time() - start_time
            )
            self.logger.log_step_completion(result)
            return result
    
    async def execute_step_2_evaluation(self) -> StepResult:
        """
        Step 2: Model Evaluation of parsing results using GPT-4o
        """
        print("🔄 Starting Step 2: Parsing Evaluation with GPT-4o")
        self.logger.log_step_start(ProcessStep.MODEL_EVALUATION_1)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self.gpt4o_agent.evaluate_parsing_response(
                self.current_context.get("original_image"),
                self.current_context.get("parsed_architecture")
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Extract score from response
            score = 0
            passed_threshold = False
            
            if response.success and response.metadata:
                score = response.metadata.get("score", 0)
                passed_threshold = score >= self.config.evaluation_threshold
            
            result = StepResult(
                step=ProcessStep.MODEL_EVALUATION_1,
                response=response,
                score=score,
                passed_threshold=passed_threshold,
                execution_time=execution_time
            )
            
            if passed_threshold:
                print(f"✅ Step 2 passed threshold with score: {score}%")
            else:
                print(f"❌ Step 2 failed threshold with score: {score}%")
            
            self.logger.log_step_completion(result)
            return result
            
        except Exception as e:
            print(f"❌ Step 2 error: {str(e)}")
            result = StepResult(
                step=ProcessStep.MODEL_EVALUATION_1,
                response=AgentResponse(content="", success=False, error_message=str(e)),
                execution_time=asyncio.get_event_loop().time() - start_time
            )
            self.logger.log_step_completion(result)
            return result
    
    async def execute_step_3_terraform_creation(self) -> StepResult:
        """
        Step 3: Terraform Creation using Claude
        """
        print("🔄 Starting Step 3: Terraform Creation with Claude")
        self.logger.log_step_start(ProcessStep.TERRAFORM_CREATION)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self.claude_agent.safe_process(
                self.current_context.get("parsed_architecture")
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            result = StepResult(
                step=ProcessStep.TERRAFORM_CREATION,
                response=response,
                execution_time=execution_time
            )
            
            if response.success:
                self.current_context["terraform_code"] = response.content
                print("✅ Step 3 completed successfully")
            else:
                print(f"❌ Step 3 failed: {response.error_message}")
            
            self.logger.log_step_completion(result)
            return result
            
        except Exception as e:
            print(f"❌ Step 3 error: {str(e)}")
            result = StepResult(
                step=ProcessStep.TERRAFORM_CREATION,
                response=AgentResponse(content="", success=False, error_message=str(e)),
                execution_time=asyncio.get_event_loop().time() - start_time
            )
            self.logger.log_step_completion(result)
            return result
    
    async def execute_step_4_terraform_evaluation(self) -> StepResult:
        """
        Step 4: Terraform Evaluation of generated code using GPT-4o
        """
        print("🔄 Starting Step 4: Terraform Evaluation with GPT-4o")
        self.logger.log_step_start(ProcessStep.MODEL_EVALUATION_2)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self.gpt4o_agent.evaluate_terraform_response(
                self.current_context.get("parsed_architecture"),
                self.current_context.get("terraform_code")
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Extract score from response
            score = 0
            passed_threshold = False
            
            if response.success and response.metadata:
                score = response.metadata.get("score", 0)
                passed_threshold = score >= self.config.evaluation_threshold
            
            result = StepResult(
                step=ProcessStep.MODEL_EVALUATION_2,
                response=response,
                score=score,
                passed_threshold=passed_threshold,
                execution_time=execution_time
            )
            
            if passed_threshold:
                print(f"✅ Step 4 passed threshold with score: {score}%")
            else:
                print(f"❌ Step 4 failed threshold with score: {score}%")
            
            self.logger.log_step_completion(result)
            return result
            
        except Exception as e:
            print(f"❌ Step 4 error: {str(e)}")
            result = StepResult(
                step=ProcessStep.MODEL_EVALUATION_2,
                response=AgentResponse(content="", success=False, error_message=str(e)),
                execution_time=asyncio.get_event_loop().time() - start_time
            )
            self.logger.log_step_completion(result)
            return result

    async def execute_full_process(self, image_input: Any) -> List[StepResult]:
        """
        Execute the automated 4-step process with threshold checks
        Steps 5 & 6 (Terraform Execution and Infrastructure Deployment) are manual
        """
        print("🚀 Starting automated orchestration process (Steps 1-4)")
        self.step_results = []
        
        try:
            # Step 1: Image Parsing
            step1_result = await self.execute_step_1_image_parsing(image_input)
            self.step_results.append(step1_result)
            
            if not step1_result.response.success:
                print("🛑 Step 1 failed, stopping process")
                self._finalize_logging()
                return self.step_results
            
            # Step 2: Evaluation with threshold check
            step2_result = await self.execute_step_2_evaluation()
            self.step_results.append(step2_result)
            
            if not step2_result.passed_threshold:
                print(f"🛑 Step 2 failed threshold check (score: {step2_result.score}%)")
                self._finalize_logging()
                return self.step_results
            
            # Step 3: Terraform Creation
            step3_result = await self.execute_step_3_terraform_creation()
            self.step_results.append(step3_result)
            
            if not step3_result.response.success:
                print("🛑 Step 3 failed, stopping process")
                self._finalize_logging()
                return self.step_results
            
            # Step 4: Terraform Evaluation with threshold check
            step4_result = await self.execute_step_4_terraform_evaluation()
            self.step_results.append(step4_result)
            
            if not step4_result.passed_threshold:
                print(f"🛑 Step 4 failed threshold check (score: {step4_result.score}%)")
                self._finalize_logging()
                return self.step_results
            
            print("🎉 Automated orchestration process completed successfully")
            print("✋ Manual steps required:")
            print("   Step 5: Execute Terraform (terraform apply)")
            print("   Step 6: Deploy to AWS Infrastructure")
            
            self._finalize_logging()
            return self.step_results
            
        except Exception as e:
            print(f"❌ Orchestration process error: {str(e)}")
            self._finalize_logging()
            raise
    
    def _finalize_logging(self):
        """Finalize the logging session"""
        summary = self.get_process_summary()
        self.logger.log_session_summary(summary)
        
        # Print log file locations
        log_files = self.logger.get_log_files()
        print(f"\n📋 Detailed execution log: {log_files['markdown_log']}")
        print(f"📊 Structured data: {log_files['json_data']}")

    def get_manual_instructions(self) -> Dict[str, Any]:
        """Get instructions for manual steps 5 & 6"""
        if not self.current_context.get("terraform_code"):
            return {"error": "No Terraform code generated. Complete automated steps first."}
        
        return {
            "status": "automated_steps_complete",
            "next_manual_steps": {
                "step_5": {
                    "name": "Terraform Execution",
                    "description": "Execute the generated Terraform code",
                    "instructions": [
                        "1. Navigate to output/terraform directory",
                        "2. Initialize Terraform: terraform init",
                        "3. Plan the deployment: terraform plan",
                        "4. Review the plan carefully",
                        "5. Apply if satisfied: terraform apply"
                    ],
                    "terraform_code_location": "output/terraform/"
                },
                "step_6": {
                    "name": "Infrastructure Deployment",
                    "description": "Deploy and validate AWS infrastructure",
                    "instructions": [
                        "1. Verify AWS credentials are configured",
                        "2. Confirm all resources were created successfully",
                        "3. Test the deployed infrastructure",
                        "4. Monitor deployment in AWS Console",
                        "5. Validate architecture matches the original diagram"
                    ]
                }
            },
            "terraform_files_location": "output/terraform/",
            "architecture_summary": self.current_context.get("parsed_architecture", "")
        }

    def get_process_summary(self) -> Dict[str, Any]:
        """Get a summary of the automated process execution (Steps 1-4)"""
        total_steps = len(self.step_results)
        successful_steps = sum(1 for result in self.step_results if result.response.success)
        failed_steps = total_steps - successful_steps
        
        # Get threshold scores
        step_2_score = None
        step_4_score = None
        
        for result in self.step_results:
            if result.step == ProcessStep.MODEL_EVALUATION_1:
                step_2_score = result.score
            elif result.step == ProcessStep.MODEL_EVALUATION_2:
                step_4_score = result.score
        
        return {
            "process_type": "automated_only",
            "total_automated_steps": total_steps,
            "max_automated_steps": 4,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "total_execution_time": sum(result.execution_time for result in self.step_results),
            "threshold_checks": {
                "step_2_score": step_2_score,
                "step_4_score": step_4_score,
                "evaluation_threshold": self.config.evaluation_threshold
            },
            "manual_steps_pending": {
                "step_5": "Terraform Execution (Manual)",
                "step_6": "Infrastructure Deployment (Manual)"
            },
            "ready_for_manual_execution": all(
                result.response.success for result in self.step_results
            ) and len(self.step_results) == 4
        }


def load_config_from_env() -> OrchestrationConfig:
    """Load configuration from environment variables"""
    from dotenv import load_dotenv
    load_dotenv()
    
    return OrchestrationConfig(
        evaluation_threshold=float(os.getenv("EVALUATION_THRESHOLD", "80")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        enable_parallel_execution=os.getenv("ENABLE_PARALLEL_EXECUTION", "true").lower() == "true",
        timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "300")),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
        gpt4_model=os.getenv("GPT4_MODEL", "gpt-4o"),
        claude_model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    )
