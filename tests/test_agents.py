"""
Tests for individual agents
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.agents.base_agent import BaseAgent, AgentResponse
from src.agents.gemini_agent import GeminiAgent
from src.agents.gpt4o_agent import GPT4oAgent
from src.agents.claude_agent import ClaudeAgent


class TestBaseAgent:
    """Test cases for BaseAgent"""
    
    def test_agent_initialization(self):
        """Test base agent initialization"""
        
        class TestAgent(BaseAgent):
            async def initialize(self):
                pass
            
            async def process(self, input_data, context=None):
                return AgentResponse(content="test", success=True)
        
        agent = TestAgent("Test Agent", "test-model", "test-key")
        
        assert agent.name == "Test Agent"
        assert agent.model == "test-model"
        assert agent.api_key == "test-key"
        assert str(agent) == "Test Agent (test-model)"
    
    @pytest.mark.asyncio
    async def test_safe_process_success(self):
        """Test safe_process with successful execution"""
        
        class TestAgent(BaseAgent):
            async def initialize(self):
                pass
            
            async def process(self, input_data, context=None):
                return AgentResponse(content="success", success=True)
        
        agent = TestAgent("Test Agent", "test-model", "test-key")
        result = await agent.safe_process("test_input")
        
        assert result.success
        assert result.content == "success"
    
    @pytest.mark.asyncio
    async def test_safe_process_error(self):
        """Test safe_process with error handling"""
        
        class TestAgent(BaseAgent):
            async def initialize(self):
                pass
            
            async def process(self, input_data, context=None):
                raise Exception("Test error")
        
        agent = TestAgent("Test Agent", "test-model", "test-key")
        result = await agent.safe_process("test_input")
        
        assert not result.success
        assert "Test error" in result.error_message


class TestAgentResponse:
    """Test cases for AgentResponse"""
    
    def test_agent_response_success(self):
        """Test successful AgentResponse"""
        response = AgentResponse(
            content="test content",
            confidence=0.95,
            metadata={"key": "value"},
            success=True
        )
        
        assert response.content == "test content"
        assert response.confidence == 0.95
        assert response.metadata == {"key": "value"}
        assert response.success is True
        assert response.error_message is None
    
    def test_agent_response_error(self):
        """Test error AgentResponse"""
        response = AgentResponse(
            content="",
            success=False,
            error_message="Test error"
        )
        
        assert response.content == ""
        assert response.success is False
        assert response.error_message == "Test error"
        assert response.confidence is None
        assert response.metadata == {}


class TestGeminiAgent:
    """Test cases for GeminiAgent"""
    
    def test_gemini_agent_initialization(self):
        """Test Gemini agent initialization"""
        agent = GeminiAgent("test_api_key", "gemini-1.5-pro")
        
        assert agent.name == "Gemini Vision Agent"
        assert agent.model == "gemini-1.5-pro"
        assert agent.api_key == "test_api_key"
    
    @pytest.mark.asyncio
    async def test_gemini_initialize(self):
        """Test Gemini agent initialization"""
        agent = GeminiAgent("test_api_key")
        
        with patch('google.generativeai.configure') as mock_configure:
            with patch('google.generativeai.GenerativeModel') as mock_model:
                await agent.initialize()
                
                mock_configure.assert_called_once_with(api_key="test_api_key")
                mock_model.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_gemini_process_success(self):
        """Test Gemini agent processing"""
        agent = GeminiAgent("test_api_key")
        
        # Mock the client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Parsed architecture data"
        mock_client.generate_content_async = AsyncMock(return_value=mock_response)
        agent.client = mock_client
        
        with patch('PIL.Image.open') as mock_image_open:
            mock_image_open.return_value = Mock()
            
            result = await agent.process("test_image.jpg")
            
            assert result.success
            assert result.content == "Parsed architecture data"
            assert result.confidence == 0.95
            assert result.metadata["task"] == "architecture_image_parsing"


class TestGPT4oAgent:
    """Test cases for GPT4oAgent"""
    
    def test_gpt4o_agent_initialization(self):
        """Test GPT-4o agent initialization"""
        agent = GPT4oAgent("test_api_key", "gpt-4o")
        
        assert agent.name == "GPT-4o Evaluation Agent"
        assert agent.model == "gpt-4o"
        assert agent.api_key == "test_api_key"
    
    @pytest.mark.asyncio
    async def test_gpt4o_initialize(self):
        """Test GPT-4o agent initialization"""
        agent = GPT4oAgent("test_api_key")
        
        with patch('openai.AsyncOpenAI') as mock_openai:
            await agent.initialize()
            mock_openai.assert_called_once_with(api_key="test_api_key")
    
    @pytest.mark.asyncio
    async def test_gpt4o_evaluate_parsing_response(self):
        """Test GPT-4o parsing evaluation"""
        agent = GPT4oAgent("test_api_key")
        
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = '{"overall_score": 85, "pass_threshold": true}'
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        agent.client = mock_client
        
        result = await agent.evaluate_parsing_response("original_input", "parsing_response")
        
        assert result.success
        assert result.metadata["score"] == 85
        assert result.metadata["task"] == "parsing_evaluation"
    
    @pytest.mark.asyncio
    async def test_gpt4o_evaluate_terraform_response(self):
        """Test GPT-4o Terraform evaluation"""
        agent = GPT4oAgent("test_api_key")
        
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = '{"overall_score": 90, "pass_threshold": true}'
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        agent.client = mock_client
        
        result = await agent.evaluate_terraform_response("requirements", "terraform_code")
        
        assert result.success
        assert result.metadata["score"] == 90
        assert result.metadata["task"] == "terraform_evaluation"


class TestClaudeAgent:
    """Test cases for ClaudeAgent"""
    
    def test_claude_agent_initialization(self):
        """Test Claude agent initialization"""
        agent = ClaudeAgent("test_api_key", "claude-3-5-sonnet-20241022")
        
        assert agent.name == "Claude Terraform Agent"
        assert agent.model == "claude-3-5-sonnet-20241022"
        assert agent.api_key == "test_api_key"
    
    @pytest.mark.asyncio
    async def test_claude_initialize(self):
        """Test Claude agent initialization"""
        agent = ClaudeAgent("test_api_key")
        
        with patch('anthropic.AsyncAnthropic') as mock_anthropic:
            await agent.initialize()
            mock_anthropic.assert_called_once_with(api_key="test_api_key")
    
    @pytest.mark.asyncio
    async def test_claude_process_success(self):
        """Test Claude agent processing"""
        agent = ClaudeAgent("test_api_key")
        
        # Mock Anthropic client
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated Terraform code"
        mock_response.content = [mock_content]
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        agent.client = mock_client
        
        result = await agent.process("architecture_requirements")
        
        assert result.success
        assert result.content == "Generated Terraform code"
        assert result.confidence == 0.90
        assert result.metadata["task"] == "terraform_generation"


class TestOrchestrator:
    """Test cases for the Orchestrator"""
    
    @pytest.mark.asyncio
    async def test_full_automated_process_success(self, orchestrator):
        """Test successful automated process execution (Steps 1-4 only)"""
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
        
        assert len(results) == 4  # Only 4 automated steps
        assert all(result.response.success for result in results)
        
        # Check threshold results
        assert results[1].passed_threshold  # Step 2 evaluation
        assert results[3].passed_threshold  # Step 4 evaluation

    def test_manual_instructions(self, orchestrator):
        """Test manual instructions generation"""
        # Setup context with terraform code
        orchestrator.current_context = {
            "terraform_code": "resource \"aws_s3_bucket\" \"test\" {}",
            "parsed_architecture": "Test architecture"
        }
        
        instructions = orchestrator.get_manual_instructions()
        
        assert instructions["status"] == "automated_steps_complete"
        assert "step_5" in instructions["next_manual_steps"]
        assert "step_6" in instructions["next_manual_steps"]
        assert "Terraform Execution" in instructions["next_manual_steps"]["step_5"]["name"]
        assert "Infrastructure Deployment" in instructions["next_manual_steps"]["step_6"]["name"]


if __name__ == "__main__":
    pytest.main([__file__])
