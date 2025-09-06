"""
AGI Agent - A general-purpose artificial general intelligence agent
capable of completing complex tasks and inventing solutions.
"""

__version__ = "0.1.0"
__author__ = "AGI Agent Development Team"

from .core.reasoning_engine import ReasoningEngine
from .core.task_planner import TaskPlanner
from .core.knowledge_manager import KnowledgeManager
from .core.tool_integration import ToolIntegrationFramework
from .core.learning_system import LearningSystem
from .core.safety_controller import SafetyController
from .interfaces.communication import CommunicationInterface
from .agent import AGIAgent, AgentConfig

__all__ = [
    "ReasoningEngine",
    "TaskPlanner", 
    "KnowledgeManager",
    "ToolIntegrationFramework",
    "LearningSystem",
    "SafetyController",
    "CommunicationInterface",
    "AGIAgent",
    "AgentConfig"
]
