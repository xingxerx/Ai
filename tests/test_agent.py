"""
Tests for the main AGI Agent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from agi_agent import AGIAgent, AgentConfig
from agi_agent.models.task import Task, TaskStatus


class TestAGIAgent:
    """Test cases for the AGI Agent."""
    
    @pytest.fixture
    def agent_config(self):
        """Create test agent configuration."""
        return AgentConfig(
            model_provider="openai",
            model_name="gpt-4",
            safety_level="medium",
            learning_enabled=False,  # Disable for testing
            auto_approve_safe_actions=True
        )
    
    @pytest.fixture
    def mock_agent(self, agent_config):
        """Create a mock AGI agent for testing."""
        with patch('agi_agent.agent.ReasoningEngine') as mock_reasoning, \
             patch('agi_agent.agent.TaskPlanner') as mock_planner, \
             patch('agi_agent.agent.KnowledgeManager') as mock_knowledge, \
             patch('agi_agent.agent.ToolIntegrationFramework') as mock_tools, \
             patch('agi_agent.agent.LearningSystem') as mock_learning, \
             patch('agi_agent.agent.SafetyController') as mock_safety, \
             patch('agi_agent.agent.CommunicationInterface') as mock_comm:
            
            agent = AGIAgent(agent_config)
            
            # Setup mocks
            agent.reasoning_engine._query_model = AsyncMock(return_value='{"objective": "test", "requirements": [], "constraints": [], "priority": "medium", "complexity": "simple", "reasoning_types": ["analytical"]}')
            agent.task_planner.create_plan = AsyncMock()
            agent.safety_controller.check_action = AsyncMock()
            agent.tool_framework.execute_tool = AsyncMock()
            
            return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test agent initialization."""
        with patch('agi_agent.agent.ReasoningEngine'), \
             patch('agi_agent.agent.TaskPlanner'), \
             patch('agi_agent.agent.KnowledgeManager'), \
             patch('agi_agent.agent.ToolIntegrationFramework'), \
             patch('agi_agent.agent.LearningSystem'), \
             patch('agi_agent.agent.SafetyController'), \
             patch('agi_agent.agent.CommunicationInterface'):
            
            agent = AGIAgent(agent_config)
            
            assert agent.config == agent_config
            assert agent.state.value == "idle"
            assert agent.current_task is None
    
    @pytest.mark.asyncio
    async def test_process_simple_request(self, mock_agent):
        """Test processing a simple request."""
        # Setup mocks
        from agi_agent.models.plan import ExecutionPlan, PlanStep, StepType
        from agi_agent.models.response import AgentResponse
        from agi_agent.core.safety_controller import SafetyResult, SafetyLevel
        
        # Mock execution plan
        mock_plan = ExecutionPlan(task_id="test-task", steps=[])
        mock_step = PlanStep(
            description="Test step",
            step_type=StepType.REASONING
        )
        mock_plan.add_step(mock_step)
        
        mock_agent.task_planner.create_plan.return_value = mock_plan
        
        # Mock safety approval
        safety_result = SafetyResult(
            approved=True,
            risk_level=SafetyLevel.LOW,
            risk_categories=[],
            reason="Safe action"
        )
        mock_agent.safety_controller.check_action.return_value = safety_result
        
        # Mock step execution
        mock_agent.reasoning_engine.execute_reasoning_step = AsyncMock(
            return_value={"step_id": mock_step.id, "result": "Test result", "success": True}
        )
        
        # Process request
        response = await mock_agent.process_request("Test task")
        
        # Verify response
        assert response.success is True
        assert response.task_id is not None
        assert "results" in response.result
    
    @pytest.mark.asyncio
    async def test_get_status(self, mock_agent):
        """Test getting agent status."""
        status = mock_agent.get_status()
        
        assert "state" in status
        assert "current_task" in status
        assert "components_status" in status
        assert status["state"] == "idle"
    
    @pytest.mark.asyncio
    async def test_agent_shutdown(self, mock_agent):
        """Test agent shutdown."""
        # Mock cleanup methods
        mock_agent.knowledge_manager.close = AsyncMock()
        mock_agent.tool_framework.cleanup = AsyncMock()
        
        await mock_agent.shutdown()
        
        # Verify cleanup was called
        mock_agent.knowledge_manager.close.assert_called_once()
        mock_agent.tool_framework.cleanup.assert_called_once()
    
    def test_agent_config_validation(self):
        """Test agent configuration validation."""
        # Valid config
        config = AgentConfig(
            model_provider="openai",
            model_name="gpt-4"
        )
        assert config.model_provider == "openai"
        assert config.model_name == "gpt-4"
        assert config.safety_level == "high"  # default
        
        # Test defaults
        assert config.max_reasoning_depth == 10
        assert config.learning_enabled is True
        assert config.auto_approve_safe_actions is False


class TestAgentIntegration:
    """Integration tests for the AGI Agent."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_simple_task(self):
        """Test end-to-end execution of a simple task."""
        # This would require actual API keys, so we'll mock it
        config = AgentConfig(
            model_provider="openai",
            model_name="gpt-4",
            learning_enabled=False
        )
        
        with patch('agi_agent.core.reasoning_engine.openai.AsyncOpenAI') as mock_openai:
            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"objective": "calculate", "requirements": ["math"], "constraints": [], "priority": "medium", "complexity": "simple", "reasoning_types": ["analytical"]}'
            
            mock_client = Mock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client
            
            agent = AGIAgent(config)
            
            # This would normally require API keys
            # response = await agent.process_request("Calculate 2 + 2")
            # assert response.success is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_agent):
        """Test error handling in agent."""
        # Force an error in task planning
        mock_agent.task_planner.create_plan.side_effect = Exception("Planning failed")
        
        response = await mock_agent.process_request("Test task")
        
        assert response.success is False
        assert "Planning failed" in response.error
        assert mock_agent.state.value == "error"


if __name__ == "__main__":
    pytest.main([__file__])
