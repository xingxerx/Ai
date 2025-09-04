"""
Tool integration framework for the AGI Agent.
Manages discovery, registration, and execution of external tools.
"""

import json
# Optional dependency: PyYAML for config loading
try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # type: ignore
import logging
import importlib
# The user may need to install this dependency: pip install pyautogui
# Optional dependency: pyautogui for sending hotkeys
try:
    import pyautogui  # type: ignore
except Exception:
    pyautogui = None  # type: ignore
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class ToolDefinition:
    """Definition of a tool that can be used by the agent."""
    name: str
    description: str
    parameters: Dict[str, Any]
    return_type: str
    category: str = "general"
    safety_level: str = "medium"  # low, medium, high
    requires_approval: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "category": self.category,
            "safety_level": self.safety_level,
            "requires_approval": self.requires_approval
        }


class BaseTool(ABC):
    """Base class for all tools."""
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """Get the tool definition."""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate tool parameters."""
        return True


class ToolIntegrationFramework:
    """
    Framework for integrating and managing external tools.
    """
    
    def __init__(self, config_path: str = "./tools.yaml"):
        self.config_path = config_path
        self.tools: Dict[str, BaseTool] = {}
        self.tool_definitions: Dict[str, ToolDefinition] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize built-in tools
        self._initialize_builtin_tools()
        
        # Load external tools from config
        self._load_tools_from_config()
    
    def _initialize_builtin_tools(self):
        """Initialize built-in tools."""
        # Web search tool
        self.register_tool("web_search", WebSearchTool())
        
        # File operations
        self.register_tool("file_read", FileReadTool())
        self.register_tool("file_write", FileWriteTool())
        
        # Code execution
        self.register_tool("python_exec", PythonExecutionTool())
        
        # Calculator
        self.register_tool("calculator", CalculatorTool())
        self.register_tool("kill_program", KillProgramTool())
        
        self.logger.info(f"Initialized {len(self.tools)} built-in tools")
    
    def _load_tools_from_config(self):
        """Load external tools from configuration file."""
        # If PyYAML is not available, skip external config gracefully
        if yaml is None:
            self.logger.info(
                "PyYAML not installed; skipping external tools config at %s",
                self.config_path,
            )
            return
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

            for tool_config in config.get('tools', []) or []:
                self._load_external_tool(tool_config)

        except FileNotFoundError:
            self.logger.info(
                "Tool config file %s not found, using built-in tools only", self.config_path
            )
        except Exception as e:
            self.logger.error(f"Error loading tool config: {e}")
    
    def _load_external_tool(self, tool_config: Dict[str, Any]):
        """Load an external tool from configuration."""
        try:
            module_name = tool_config.get('module')
            class_name = tool_config.get('class')
            
            if module_name and class_name:
                module = importlib.import_module(module_name)
                tool_class = getattr(module, class_name)
                tool_instance = tool_class(**tool_config.get('init_params', {}))
                
                self.register_tool(tool_config['name'], tool_instance)
                self.logger.info(f"Loaded external tool: {tool_config['name']}")
        
        except Exception as e:
            self.logger.error(f"Failed to load external tool {tool_config.get('name', 'unknown')}: {e}")
    
    def register_tool(self, name: str, tool: BaseTool):
        """Register a tool with the framework."""
        self.tools[name] = tool
        self.tool_definitions[name] = tool.get_definition()
        self.logger.debug(f"Registered tool: {name}")
    
    def get_available_tools(self) -> List[ToolDefinition]:
        """Get list of available tools."""
        return list(self.tool_definitions.values())
    
    def get_tool_definition(self, name: str) -> Optional[ToolDefinition]:
        """Get definition for a specific tool."""
        return self.tool_definitions.get(name)
    
    async def execute_tool(self, name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        if name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        tool = self.tools[name]
        
        # Validate parameters
        if not tool.validate_parameters(parameters):
            return {
                "success": False,
                "error": f"Invalid parameters for tool '{name}'",
                "expected_parameters": tool.get_definition().parameters
            }
        
        try:
            self.logger.info(f"Executing tool: {name}")
            result = await tool.execute(parameters)
            
            return {
                "success": True,
                "tool_name": name,
                "result": result,
                "parameters_used": parameters
            }
        
        except Exception as e:
            self.logger.error(f"Error executing tool {name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": name
            }
    
    async def cleanup(self):
        """Cleanup resources used by tools."""
        for tool in self.tools.values():
            if hasattr(tool, 'cleanup'):
                try:
                    await tool.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up tool: {e}")


# Built-in tool implementations

class WebSearchTool(BaseTool):
    """Tool for web searching."""
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        query = parameters.get("query", "")
        max_results = parameters.get("max_results", 5)
        
        # Placeholder implementation
        return {
            "query": query,
            "results": [
                {"title": f"Result {i}", "url": f"https://example.com/{i}", "snippet": f"Snippet for {query}"}
                for i in range(min(max_results, 3))
            ]
        }
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="web_search",
            description="Search the web for information",
            parameters={
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Maximum number of results", "default": 5}
            },
            return_type="object",
            category="information",
            safety_level="low"
        )


class FileReadTool(BaseTool):
    """Tool for reading files."""
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        file_path = parameters.get("file_path", "")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "file_path": file_path,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="file_read",
            description="Read content from a file",
            parameters={
                "file_path": {"type": "string", "description": "Path to the file to read"}
            },
            return_type="object",
            category="file_system",
            safety_level="medium"
        )


class FileWriteTool(BaseTool):
    """Tool for writing files."""
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        file_path = parameters.get("file_path", "")
        content = parameters.get("content", "")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8')),
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="file_write",
            description="Write content to a file",
            parameters={
                "file_path": {"type": "string", "description": "Path to the file to write"},
                "content": {"type": "string", "description": "Content to write to the file"}
            },
            return_type="object",
            category="file_system",
            safety_level="high",
            requires_approval=True
        )


class PythonExecutionTool(BaseTool):
    """Tool for executing Python code."""
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        code = parameters.get("code", "")
        
        # This is a placeholder - in a real implementation, you'd want to use
        # a sandboxed environment for code execution
        return {
            "code": code,
            "output": "Code execution not implemented in this demo",
            "success": False,
            "note": "Code execution requires sandboxed environment"
        }
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="python_exec",
            description="Execute Python code",
            parameters={
                "code": {"type": "string", "description": "Python code to execute"}
            },
            return_type="object",
            category="computation",
            safety_level="high",
            requires_approval=True
        )


class CalculatorTool(BaseTool):
    """Tool for mathematical calculations."""
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        expression = parameters.get("expression", "")
        
        try:
            # Simple evaluation - in production, use a safer math parser
            result = eval(expression, {"__builtins__": {}}, {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "sqrt": lambda x: x**0.5
            })
            
            return {
                "expression": expression,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "success": False
            }
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="calculator",
            description="Perform mathematical calculations",
            parameters={
                "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
            },
            return_type="object",
            category="computation",
            safety_level="low"
        )


class KillProgramTool(BaseTool):
    """Tool for killing the foreground program."""

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if pyautogui is None:
                return {
                    "success": False,
                    "error": "pyautogui is not installed. Install with: pip install pyautogui"
                }
            pyautogui.hotkey('alt', 'f4')
            return {
                "success": True,
                "message": "Sent Alt+F4 hotkey."
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="kill_program",
            description="Sends the Alt+F4 hotkey to the operating system to close the current active window.",
            parameters={},
            return_type="object",
            category="system",
            safety_level="high",
            requires_approval=True
        )
