"""
Planning-related data models.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class StepType(Enum):
    REASONING = "reasoning"
    TOOL_CALL = "tool_call"
    DECISION = "decision"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"


class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """Represents a single step in an execution plan."""
    
    description: str
    step_type: StepType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_number: int = 0
    status: StepStatus = StepStatus.PENDING
    
    # Step configuration
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_output: Optional[str] = None
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Step IDs
    
    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Metadata
    estimated_duration: Optional[int] = None  # in seconds
    actual_duration: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def start(self):
        """Mark step as started."""
        self.status = StepStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete(self, result: Dict[str, Any]):
        """Mark step as completed."""
        self.status = StepStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.actual_duration = int(duration)
    
    def fail(self, error: str):
        """Mark step as failed."""
        self.status = StepStatus.FAILED
        self.error = error
        self.retry_count += 1
    
    def skip(self):
        """Mark step as skipped."""
        self.status = StepStatus.SKIPPED
    
    def can_retry(self) -> bool:
        """Check if step can be retried."""
        return self.retry_count < self.max_retries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "step_type": self.step_type.value,
            "step_number": self.step_number,
            "status": self.status.value,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "expected_output": self.expected_output,
            "depends_on": self.depends_on,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }


@dataclass
class ExecutionPlan:
    """Represents a complete execution plan for a task."""
    
    task_id: str
    steps: List[PlanStep]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    # Plan metadata
    description: Optional[str] = None
    estimated_total_duration: Optional[int] = None  # in seconds
    actual_total_duration: Optional[int] = None
    
    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None  # Step ID
    
    def add_step(self, step: PlanStep):
        """Add a step to the plan."""
        step.step_number = len(self.steps) + 1
        self.steps.append(step)
    
    def get_next_step(self) -> Optional[PlanStep]:
        """Get the next step to execute."""
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                # Check if dependencies are satisfied
                if self._dependencies_satisfied(step):
                    return step
        return None
    
    def get_step_by_id(self, step_id: str) -> Optional[PlanStep]:
        """Get a step by its ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def _dependencies_satisfied(self, step: PlanStep) -> bool:
        """Check if all dependencies for a step are satisfied."""
        for dep_id in step.depends_on:
            dep_step = self.get_step_by_id(dep_id)
            if not dep_step or dep_step.status != StepStatus.COMPLETED:
                return False
        return True
    
    def get_progress(self) -> Dict[str, Any]:
        """Get execution progress."""
        total_steps = len(self.steps)
        completed_steps = sum(1 for step in self.steps if step.status == StepStatus.COMPLETED)
        failed_steps = sum(1 for step in self.steps if step.status == StepStatus.FAILED)
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            "current_step": self.current_step
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "current_step": self.current_step,
            "estimated_total_duration": self.estimated_total_duration,
            "actual_total_duration": self.actual_total_duration,
            "steps": [step.to_dict() for step in self.steps],
            "progress": self.get_progress()
        }
