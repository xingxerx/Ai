"""
Safety controller for the AGI Agent.
Implements safety mechanisms and human oversight.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from ..models.plan import PlanStep


class SafetyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(Enum):
    DATA_ACCESS = "data_access"
    SYSTEM_MODIFICATION = "system_modification"
    NETWORK_ACCESS = "network_access"
    CODE_EXECUTION = "code_execution"
    FILE_OPERATIONS = "file_operations"
    EXTERNAL_COMMUNICATION = "external_communication"


@dataclass
class SafetyResult:
    """Result of a safety check."""
    approved: bool
    risk_level: SafetyLevel
    risk_categories: List[RiskCategory]
    reason: str
    requires_human_approval: bool = False
    suggested_modifications: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved": self.approved,
            "risk_level": self.risk_level.value,
            "risk_categories": [cat.value for cat in self.risk_categories],
            "reason": self.reason,
            "requires_human_approval": self.requires_human_approval,
            "suggested_modifications": self.suggested_modifications or []
        }


class SafetyController:
    """
    Safety controller that evaluates and controls agent actions.
    """
    
    def __init__(self, level: str = "high", auto_approve_safe: bool = False):
        self.safety_level = SafetyLevel(level)
        self.auto_approve_safe = auto_approve_safe
        self.logger = logging.getLogger(__name__)
        
        # Safety rules and policies
        self.safety_rules = self._initialize_safety_rules()
        self.risk_assessments = self._initialize_risk_assessments()
        
        self.logger.info(f"Safety controller initialized with level: {level}")
    
    def _initialize_safety_rules(self) -> Dict[str, Any]:
        """Initialize safety rules based on safety level."""
        base_rules = {
            "max_file_size_mb": 100,
            "allowed_file_extensions": [".txt", ".json", ".yaml", ".md", ".py", ".js", ".html", ".css"],
            "blocked_domains": ["localhost", "127.0.0.1", "0.0.0.0"],
            "max_network_requests": 10,
            "max_execution_time_seconds": 300
        }
        
        if self.safety_level == SafetyLevel.HIGH:
            base_rules.update({
                "require_approval_for_file_write": True,
                "require_approval_for_code_execution": True,
                "require_approval_for_network_access": True,
                "max_file_size_mb": 10,
                "max_network_requests": 5
            })
        elif self.safety_level == SafetyLevel.CRITICAL:
            base_rules.update({
                "require_approval_for_file_write": True,
                "require_approval_for_code_execution": True,
                "require_approval_for_network_access": True,
                "require_approval_for_file_read": True,
                "max_file_size_mb": 1,
                "max_network_requests": 1,
                "block_all_system_modifications": True
            })
        
        return base_rules
    
    def _initialize_risk_assessments(self) -> Dict[str, Dict[str, Any]]:
        """Initialize risk assessment rules for different actions."""
        return {
            "file_write": {
                "base_risk": SafetyLevel.MEDIUM,
                "risk_factors": {
                    "executable_extension": SafetyLevel.HIGH,
                    "system_directory": SafetyLevel.CRITICAL,
                    "large_file": SafetyLevel.MEDIUM
                }
            },
            "file_read": {
                "base_risk": SafetyLevel.LOW,
                "risk_factors": {
                    "system_file": SafetyLevel.HIGH,
                    "config_file": SafetyLevel.MEDIUM,
                    "large_file": SafetyLevel.LOW
                }
            },
            "code_execution": {
                "base_risk": SafetyLevel.HIGH,
                "risk_factors": {
                    "system_calls": SafetyLevel.CRITICAL,
                    "network_access": SafetyLevel.HIGH,
                    "file_operations": SafetyLevel.MEDIUM
                }
            },
            "network_request": {
                "base_risk": SafetyLevel.MEDIUM,
                "risk_factors": {
                    "external_domain": SafetyLevel.MEDIUM,
                    "post_request": SafetyLevel.HIGH,
                    "file_upload": SafetyLevel.HIGH
                }
            }
        }
    
    async def check_action(self, step: PlanStep) -> SafetyResult:
        """
        Check if an action is safe to execute.
        
        Args:
            step: The plan step to check
            
        Returns:
            SafetyResult indicating if the action is approved
        """
        try:
            # Determine action type and assess risk
            risk_assessment = await self._assess_risk(step)
            
            # Apply safety rules
            approval_result = self._apply_safety_rules(step, risk_assessment)
            
            # Log the safety check
            self.logger.info(f"Safety check for {step.description}: {approval_result.approved}")
            
            return approval_result
        
        except Exception as e:
            self.logger.error(f"Error in safety check: {e}")
            # Fail safe - deny by default
            return SafetyResult(
                approved=False,
                risk_level=SafetyLevel.HIGH,
                risk_categories=[],
                reason=f"Safety check failed: {str(e)}",
                requires_human_approval=True
            )
    
    async def _assess_risk(self, step: PlanStep) -> Dict[str, Any]:
        """Assess the risk level of a plan step."""
        risk_assessment = {
            "base_risk": SafetyLevel.LOW,
            "risk_categories": [],
            "risk_factors": []
        }
        
        # Assess based on tool name
        if step.tool_name:
            tool_risk = self._assess_tool_risk(step.tool_name, step.parameters)
            risk_assessment.update(tool_risk)
        
        # Assess based on step description
        description_risk = self._assess_description_risk(step.description)
        risk_assessment["risk_factors"].extend(description_risk)
        
        # Assess based on parameters
        param_risk = self._assess_parameter_risk(step.parameters)
        risk_assessment["risk_factors"].extend(param_risk)
        
        return risk_assessment
    
    def _assess_tool_risk(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk based on tool being used."""
        risk_assessment = {
            "base_risk": SafetyLevel.LOW,
            "risk_categories": [],
            "risk_factors": []
        }
        
        # File operations
        if "file" in tool_name.lower():
            risk_assessment["risk_categories"].append(RiskCategory.FILE_OPERATIONS)
            
            if "write" in tool_name.lower():
                risk_assessment["base_risk"] = SafetyLevel.MEDIUM
                
                # Check file path
                file_path = parameters.get("file_path", "")
                if self._is_system_path(file_path):
                    risk_assessment["risk_factors"].append("system_directory")
                    risk_assessment["base_risk"] = SafetyLevel.CRITICAL
                
                # Check file extension
                if self._is_executable_file(file_path):
                    risk_assessment["risk_factors"].append("executable_extension")
                    risk_assessment["base_risk"] = SafetyLevel.HIGH
        
        # Code execution
        if "exec" in tool_name.lower() or "run" in tool_name.lower():
            risk_assessment["risk_categories"].append(RiskCategory.CODE_EXECUTION)
            risk_assessment["base_risk"] = SafetyLevel.HIGH
            
            # Check for dangerous code patterns
            code = parameters.get("code", "")
            if self._contains_dangerous_code(code):
                risk_assessment["risk_factors"].append("system_calls")
                risk_assessment["base_risk"] = SafetyLevel.CRITICAL
        
        # Network access
        if "web" in tool_name.lower() or "http" in tool_name.lower():
            risk_assessment["risk_categories"].append(RiskCategory.NETWORK_ACCESS)
            risk_assessment["base_risk"] = SafetyLevel.MEDIUM
        
        return risk_assessment
    
    def _assess_description_risk(self, description: str) -> List[str]:
        """Assess risk based on step description."""
        risk_factors = []
        description_lower = description.lower()
        
        # Look for risky keywords
        risky_keywords = {
            "delete": "destructive_action",
            "remove": "destructive_action",
            "modify": "modification_action",
            "install": "system_modification",
            "download": "network_action",
            "execute": "execution_action",
            "run": "execution_action"
        }
        
        for keyword, risk_factor in risky_keywords.items():
            if keyword in description_lower:
                risk_factors.append(risk_factor)
        
        return risk_factors
    
    def _assess_parameter_risk(self, parameters: Dict[str, Any]) -> List[str]:
        """Assess risk based on parameters."""
        risk_factors = []
        
        # Check for URLs
        for key, value in parameters.items():
            if isinstance(value, str):
                if value.startswith(("http://", "https://")):
                    risk_factors.append("external_url")
                
                # Check for file paths
                if "/" in value or "\\" in value:
                    if self._is_system_path(value):
                        risk_factors.append("system_path")
        
        return risk_factors
    
    def _apply_safety_rules(self, step: PlanStep, risk_assessment: Dict[str, Any]) -> SafetyResult:
        """Apply safety rules to determine if action should be approved."""
        base_risk = risk_assessment["base_risk"]
        risk_categories = risk_assessment["risk_categories"]
        risk_factors = risk_assessment["risk_factors"]
        
        # Determine if approval is required
        requires_approval = False
        approved = True
        reason = "Action approved"
        
        # Check safety level requirements
        if self.safety_level == SafetyLevel.HIGH:
            if base_risk in [SafetyLevel.HIGH, SafetyLevel.CRITICAL]:
                requires_approval = True
                approved = self.auto_approve_safe
                reason = f"High-risk action requires approval: {base_risk.value}"
        
        elif self.safety_level == SafetyLevel.CRITICAL:
            if base_risk in [SafetyLevel.MEDIUM, SafetyLevel.HIGH, SafetyLevel.CRITICAL]:
                requires_approval = True
                approved = False
                reason = f"Action blocked by critical safety level: {base_risk.value}"
        
        # Check specific safety rules
        if step.tool_name == "file_write" and self.safety_rules.get("require_approval_for_file_write"):
            requires_approval = True
            if not self.auto_approve_safe:
                approved = False
            reason = "File write operations require approval"
        
        if step.tool_name == "python_exec" and self.safety_rules.get("require_approval_for_code_execution"):
            requires_approval = True
            approved = False
            reason = "Code execution requires approval"
        
        # Generate suggestions
        suggestions = self._generate_safety_suggestions(step, risk_assessment)
        
        return SafetyResult(
            approved=approved,
            risk_level=base_risk,
            risk_categories=risk_categories,
            reason=reason,
            requires_human_approval=requires_approval,
            suggested_modifications=suggestions
        )
    
    def _generate_safety_suggestions(self, step: PlanStep, risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate suggestions to make the action safer."""
        suggestions = []
        
        risk_factors = risk_assessment.get("risk_factors", [])
        
        if "system_directory" in risk_factors:
            suggestions.append("Consider using a user directory instead of system directory")
        
        if "executable_extension" in risk_factors:
            suggestions.append("Consider using a non-executable file extension")
        
        if "external_url" in risk_factors:
            suggestions.append("Verify the external URL is trusted")
        
        if "system_calls" in risk_factors:
            suggestions.append("Remove system calls from code execution")
        
        return suggestions
    
    def _is_system_path(self, path: str) -> bool:
        """Check if path is in a system directory."""
        system_paths = ["/etc", "/sys", "/proc", "/boot", "C:\\Windows", "C:\\System32"]
        return any(path.startswith(sys_path) for sys_path in system_paths)
    
    def _is_executable_file(self, path: str) -> bool:
        """Check if file has executable extension."""
        executable_extensions = [".exe", ".bat", ".sh", ".cmd", ".com", ".scr"]
        return any(path.lower().endswith(ext) for ext in executable_extensions)
    
    def _contains_dangerous_code(self, code: str) -> bool:
        """Check if code contains dangerous patterns."""
        dangerous_patterns = [
            "import os", "import subprocess", "import sys",
            "exec(", "eval(", "__import__",
            "open(", "file(", "input(",
            "rm ", "del ", "rmdir"
        ]
        return any(pattern in code for pattern in dangerous_patterns)
    
    def update_safety_level(self, level: str):
        """Update the safety level."""
        self.safety_level = SafetyLevel(level)
        self.safety_rules = self._initialize_safety_rules()
        self.logger.info(f"Safety level updated to: {level}")
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status."""
        return {
            "safety_level": self.safety_level.value,
            "auto_approve_safe": self.auto_approve_safe,
            "active_rules": len(self.safety_rules),
            "risk_categories": [cat.value for cat in RiskCategory]
        }
