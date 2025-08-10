"""
Tests for the orchestration system
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.orchestration.orchestrator import (
    MultiAgentOrchestrator, 
    OrchestrationConfig, 
    ProcessStep,
    StepResult
)
from src.agents.base_agent import AgentResponse


@pytest.fixture
def test_config():
    """Test configuration"""
    return OrchestrationConfig(
        evaluation_threshold=80.0,
        max_retries=3,
        openai_api_key="test_openai_key",
        anthropic_api_key="test_anthropic_key",
        google_api_key="test_google_key"
    )


@pytest.fixture
def orchestrator(test_config):
    """Test orchestrator instance"""
    return MultiAgentOrchestrator(test_config)


class TestMultiAgentOrchestrator:
    """Test cases for the MultiAgentOrchestrator"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator.config.evaluation_threshold == 80.0
        assert orchestrator.config.max_retries == 3
        assert len(orchestrator.step_results) == 0
        assert isinstance(orchestrator.current_context, dict)
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, orchestrator):
        """Test agent initialization"""
        with patch('src.agents.gemini_agent.GeminiAgent') as mock_gemini:
            with patch('src.agents.gpt4o_agent.GPT4oAgent') as mock_gpt4o:
                with patch('src.agents.claude_agent.ClaudeAgent') as mock_claude:
                    # Setup mocks
                    mock_gemini.return_value.initialize = AsyncMock()
                    mock_gpt4o.return_value.initialize = AsyncMock()
                    mock_claude.return_value.initialize = AsyncMock()
                    
                    await orchestrator.initialize_agents()
                    
                    # Verify agents were created and initialized
                    mock_gemini.assert_called_once()
                    mock_gpt4o.assert_called_once()
                    mock_claude.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_step_1_image_parsing_success(self, orchestrator):
        """Test successful image parsing step"""
        # Mock Gemini agent
        mock_response = AgentResponse(
            content="Parsed architecture data",
            success=True,
            confidence=0.95
        )
        
        orchestrator.gemini_agent = Mock()
        orchestrator.gemini_agent.safe_process = AsyncMock(return_value=mock_response)
        
        result = await orchestrator.execute_step_1_image_parsing("test_image.jpg")
        
        assert result.step == ProcessStep.IMAGE_PARSING
        assert result.response.success
        assert result.response.content == "Parsed architecture data"
        assert "parsed_architecture" in orchestrator.current_context
    
    @pytest.mark.asyncio
    async def test_step_2_evaluation_pass_threshold(self, orchestrator):
        """Test evaluation step passing threshold"""
        # Setup context
        orchestrator.current_context = {
            "parsed_architecture": "test data",
            "original_image": "test_image.jpg"
        }
        
        # Mock GPT-4o agent
        mock_response = AgentResponse(
            content="Evaluation result",
            success=True,
            metadata={"score": 85, "threshold_passed": True}
        )
        
        orchestrator.gpt4o_agent = Mock()
        orchestrator.gpt4o_agent.evaluate_parsing_response = AsyncMock(return_value=mock_response)
        
        result = await orchestrator.execute_step_2_evaluation()
        
        assert result.step == ProcessStep.MODEL_EVALUATION_1
        assert result.response.success
        assert result.score == 85
        assert result.passed_threshold
    
    @pytest.mark.asyncio
    async def test_step_2_evaluation_fail_threshold(self, orchestrator):
        """Test evaluation step failing threshold"""
        # Setup context
        orchestrator.current_context = {
            "parsed_architecture": "test data",
            "original_image": "test_image.jpg"
        }
        
        # Mock GPT-4o agent
        mock_response = AgentResponse(
            content="Evaluation result",
            success=True,
            metadata={"score": 75, "threshold_passed": False}
        )
        
        orchestrator.gpt4o_agent = Mock()
        orchestrator.gpt4o_agent.evaluate_parsing_response = AsyncMock(return_value=mock_response)
        
        result = await orchestrator.execute_step_2_evaluation()
        
        assert result.step == ProcessStep.MODEL_EVALUATION_1
        assert result.response.success
        assert result.score == 75
        assert not result.passed_threshold
    
    @pytest.mark.asyncio
    async def test_step_3_terraform_creation(self, orchestrator):
        """Test Terraform creation step"""
        # Setup context
        orchestrator.current_context = {
            "parsed_architecture": "test architecture data"
        }
        
        # Mock Claude agent
        mock_response = AgentResponse(
            content="Generated Terraform code",
            success=True,
            confidence=0.90
        )
        
        orchestrator.claude_agent = Mock()
        orchestrator.claude_agent.safe_process = AsyncMock(return_value=mock_response)
        
        result = await orchestrator.execute_step_3_terraform_creation()
        
        assert result.step == ProcessStep.TERRAFORM_CREATION
        assert result.response.success
        assert result.response.content == "Generated Terraform code"
        assert "terraform_code" in orchestrator.current_context
    
    @pytest.mark.asyncio
    async def test_full_process_success(self, orchestrator):
        """Test successful full process execution"""
        # Mock all agents
        orchestrator.gemini_agent = Mock()
        orchestrator.gpt4o_agent = Mock()
        orchestrator.claude_agent = Mock()
        
        # Setup successful responses
        parsing_response = AgentResponse(content="Parsed data", success=True)
        eval1_response = AgentResponse(
            content="Eval 1", 
            success=True, 
            metadata={"score": 85, "threshold_passed": True}
        )
        terraform_response = AgentResponse(content="Terraform code", success=True)
        eval2_response = AgentResponse(
            content="Eval 2", 
            success=True, 
            metadata={"score": 90, "threshold_passed": True}
        )
        
        orchestrator.gemini_agent.safe_process = AsyncMock(return_value=parsing_response)
        orchestrator.gpt4o_agent.evaluate_parsing_response = AsyncMock(return_value=eval1_response)
        orchestrator.claude_agent.safe_process = AsyncMock(return_value=terraform_response)
        orchestrator.gpt4o_agent.evaluate_terraform_response = AsyncMock(return_value=eval2_response)
        
        results = await orchestrator.execute_full_process("test_image.jpg")
        
        assert len(results) == 6  # All 6 steps should be executed
        assert all(result.response.success for result in results[:4])  # First 4 steps should succeed
        
        # Check threshold results
        assert results[1].passed_threshold  # Step 2 evaluation
        assert results[3].passed_threshold  # Step 4 evaluation
    
    @pytest.mark.asyncio
    async def test_full_process_threshold_failure(self, orchestrator):
        """Test full process stopping at threshold failure"""
        # Mock agents
        orchestrator.gemini_agent = Mock()
        orchestrator.gpt4o_agent = Mock()
        
        # Setup responses with threshold failure
        parsing_response = AgentResponse(content="Parsed data", success=True)
        eval_response = AgentResponse(
            content="Eval", 
            success=True, 
            metadata={"score": 70, "threshold_passed": False}  # Below threshold
        )
        
        orchestrator.gemini_agent.safe_process = AsyncMock(return_value=parsing_response)
        orchestrator.gpt4o_agent.evaluate_parsing_response = AsyncMock(return_value=eval_response)
        
        results = await orchestrator.execute_full_process("test_image.jpg")
        
        assert len(results) == 2  # Should stop after step 2 failure
        assert results[0].response.success  # Step 1 succeeds
        assert not results[1].passed_threshold  # Step 2 fails threshold
    
    def test_process_summary(self, orchestrator):
        """Test process summary generation"""
        # Add mock results
        result1 = StepResult(
            step=ProcessStep.IMAGE_PARSING,
            response=AgentResponse(content="test", success=True),
            execution_time=5.0
        )
        result2 = StepResult(
            step=ProcessStep.MODEL_EVALUATION_1,
            response=AgentResponse(content="test", success=True),
            score=85,
            execution_time=3.0
        )
        
        orchestrator.step_results = [result1, result2]
        
        summary = orchestrator.get_process_summary()
        
        assert summary["total_steps"] == 2
        assert summary["successful_steps"] == 2
        assert summary["failed_steps"] == 0
        assert summary["total_execution_time"] == 8.0
        assert summary["threshold_checks"]["step_2_score"] == 85


class TestStepResult:
    """Test cases for StepResult"""
    
    def test_step_result_creation(self):
        """Test StepResult creation"""
        response = AgentResponse(content="test", success=True)
        result = StepResult(
            step=ProcessStep.IMAGE_PARSING,
            response=response,
            score=85.0,
            execution_time=5.5
        )
        
        assert result.step == ProcessStep.IMAGE_PARSING
        assert result.response == response
        assert result.score == 85.0
        assert result.execution_time == 5.5
        assert result.retry_count == 0


class TestOrchestrationConfig:
    """Test cases for OrchestrationConfig"""
    
    def test_config_defaults(self):
        """Test configuration defaults"""
        config = OrchestrationConfig()
        
        assert config.evaluation_threshold == 80.0
        assert config.max_retries == 3
        assert config.enable_parallel_execution is True
        assert config.timeout_seconds == 300
    
    def test_config_custom_values(self):
        """Test configuration with custom values"""
        config = OrchestrationConfig(
            evaluation_threshold=90.0,
            max_retries=5,
            openai_api_key="custom_key"
        )
        
        assert config.evaluation_threshold == 90.0
        assert config.max_retries == 5
        assert config.openai_api_key == "custom_key"


if __name__ == "__main__":
    pytest.main([__file__])
