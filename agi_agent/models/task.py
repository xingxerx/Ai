"""
Task-related data models.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    """Represents a task to be completed by the AGI agent."""
    
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Task details
    requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    expected_output: Optional[str] = None
    
    # Execution tracking
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    estimated_duration: Optional[int] = None  # in minutes
    actual_duration: Optional[int] = None
    
    def start(self):
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
    
    def complete(self, result: Dict[str, Any]):
        """Mark task as completed with result."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        self.result = result
        
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds() / 60
            self.actual_duration = int(duration)
    
    def fail(self, error_message: str):
        """Mark task as failed with error message."""
        self.status = TaskStatus.FAILED
        self.updated_at = datetime.now()
        self.error_message = error_message
    
    def cancel(self):
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "requirements": self.requirements,
            "constraints": self.constraints,
            "context": self.context,
            "expected_output": self.expected_output,
            "assigned_to": self.assigned_to,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error_message": self.error_message,
            "tags": self.tags,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        task = cls(
            description=data["description"],
            id=data.get("id", str(uuid.uuid4())),
            status=TaskStatus(data.get("status", "pending")),
            priority=TaskPriority(data.get("priority", "medium")),
            requirements=data.get("requirements", []),
            constraints=data.get("constraints", []),
            context=data.get("context", {}),
            expected_output=data.get("expected_output"),
            assigned_to=data.get("assigned_to"),
            result=data.get("result"),
            error_message=data.get("error_message"),
            tags=data.get("tags", []),
            estimated_duration=data.get("estimated_duration"),
            actual_duration=data.get("actual_duration")
        )
        
        # Parse datetime fields
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            task.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        
        return task
