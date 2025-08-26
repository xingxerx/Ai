"""
Main AGI Agent class that orchestrates all components.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .core.reasoning_engine import ReasoningEngine
from .core.task_planner import TaskPlanner
from .core.knowledge_manager import KnowledgeManager
from .core.tool_integration import ToolIntegrationFramework
from .core.learning_system import LearningSystem
from .core.safety_controller import SafetyController
from .interfaces.communication import CommunicationInterface
from .models.task import Task, TaskStatus
from .models.response import AgentResponse


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    ERROR = "error"


@dataclass
class AgentConfig:
    """Configuration for the AGI Agent."""
    model_provider: str = "custom"
    model_name: str = "Xing"
    max_reasoning_depth: int = 10
    safety_level: str = "high"
    learning_enabled: bool = True
    auto_approve_safe_actions: bool = False
    knowledge_base_path: str = "./knowledge"
    tools_config_path: str = "./tools.yaml"


class XingAgent:
    """
    Main Xing Agent class that coordinates all subsystems to complete tasks.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.state = AgentState.IDLE
        self.current_task: Optional[Task] = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all agent components."""
        self.logger.info("Initializing AGI Agent components...")
        
        # Core reasoning and planning
        self.reasoning_engine = ReasoningEngine(
            model_provider=self.config.model_provider,
            model_name=self.config.model_name,
            max_depth=self.config.max_reasoning_depth
        )
        
        self.task_planner = TaskPlanner(
            reasoning_engine=self.reasoning_engine
        )
        
        # Knowledge and learning
        self.knowledge_manager = KnowledgeManager(
            base_path=self.config.knowledge_base_path
        )
        
        self.learning_system = LearningSystem(
            knowledge_manager=self.knowledge_manager,
            enabled=self.config.learning_enabled
        )
        
        # Tool integration and safety
        self.tool_framework = ToolIntegrationFramework(
            config_path=self.config.tools_config_path
        )
        
        self.safety_controller = SafetyController(
            level=self.config.safety_level,
            auto_approve_safe=self.config.auto_approve_safe_actions
        )
        
        # Communication interface
        self.communication = CommunicationInterface(
            reasoning_engine=self.reasoning_engine
        )
        
        self.logger.info("AGI Agent initialization complete.")
    
    async def process_request(self, user_input: str, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Process a user request and return a response.
        
        Args:
            user_input: The user's request or task description
            context: Additional context information
            
        Returns:
            AgentResponse containing the result and metadata
        """
        try:
            self.state = AgentState.THINKING
            
            # Parse and understand the request
            task = await self._parse_request(user_input, context or {})
            self.current_task = task
            
            # Plan the task execution
            self.state = AgentState.PLANNING
            execution_plan = await self.task_planner.create_plan(task)
            
            # Execute the plan
            self.state = AgentState.EXECUTING
            result = await self._execute_plan(execution_plan)
            
            # Learn from the experience
            if self.config.learning_enabled:
                self.state = AgentState.LEARNING
                await self.learning_system.learn_from_execution(task, execution_plan, result)
            
            self.state = AgentState.IDLE
            self.current_task = None
            
            return AgentResponse(
                success=True,
                result=result,
                task_id=task.id,
                execution_plan=execution_plan,
                metadata={
                    "reasoning_steps": len(execution_plan.steps),
                    "tools_used": list(result.get("tools_used", [])),
                    "safety_checks": result.get("safety_checks", 0)
                }
            )
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.logger.error(f"Error processing request: {e}")
            
            return AgentResponse(
                success=False,
                error=str(e),
                task_id=self.current_task.id if self.current_task else None
            )
    
    async def _parse_request(self, user_input: str, context: Dict[str, Any]) -> Task:
        """Parse user input into a structured task."""
        # Use reasoning engine to understand the request
        understanding = await self.reasoning_engine.understand_request(
            user_input, context
        )
        
        # Create task object
        task = Task(
            description=user_input,
            requirements=understanding.get("requirements", []),
            constraints=understanding.get("constraints", []),
            context=context,
            priority=understanding.get("priority", "medium")
        )
        
        return task
    
    async def _execute_plan(self, execution_plan) -> Dict[str, Any]:
        """Execute the planned steps."""
        results = []
        tools_used = set()
        safety_checks = 0
        
        for step in execution_plan.steps:
            # Safety check before execution
            safety_result = await self.safety_controller.check_action(step)
            safety_checks += 1
            
            if not safety_result.approved:
                if safety_result.requires_human_approval:
                    # Request human approval
                    approval = await self._request_human_approval(step, safety_result.reason)
                    if not approval:
                        continue
                else:
                    self.logger.warning(f"Action blocked by safety controller: {safety_result.reason}")
                    continue
            
            # Execute the step
            step_result = await self._execute_step(step)
            results.append(step_result)
            
            if step.tool_name:
                tools_used.add(step.tool_name)
        
        return {
            "results": results,
            "tools_used": tools_used,
            "safety_checks": safety_checks,
            "success": True
        }
    
    async def _execute_step(self, step) -> Dict[str, Any]:
        """Execute a single step in the plan."""
        if step.tool_name:
            # Use tool integration framework
            return await self.tool_framework.execute_tool(
                step.tool_name, 
                step.parameters
            )
        else:
            # Direct reasoning/computation step
            return await self.reasoning_engine.execute_reasoning_step(step)
    
    async def _request_human_approval(self, step, reason: str) -> bool:
        """Request human approval for a potentially risky action."""
        approval_request = f"""
        Action requires approval:
        Step: {step.description}
        Reason: {reason}
        
        Do you approve this action? (y/n)
        """
        
        # This would integrate with the UI to get user input
        # For now, return False (deny by default)
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "state": self.state.value,
            "current_task": self.current_task.description if self.current_task else None,
            "components_status": {
                "reasoning_engine": "active",
                "task_planner": "active", 
                "knowledge_manager": "active",
                "tool_framework": "active",
                "safety_controller": "active",
                "learning_system": "active" if self.config.learning_enabled else "disabled"
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown the agent."""
        self.logger.info("Shutting down AGI Agent...")
        self.state = AgentState.IDLE
        
        # Cleanup components
        await self.knowledge_manager.close()
        await self.tool_framework.cleanup()
        
        self.logger.info("AGI Agent shutdown complete.")
