"""
Response-related data models.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class AgentResponse:
    """Response from the AGI agent."""
    
    success: bool
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Response content
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    # Task tracking
    task_id: Optional[str] = None
    execution_plan: Optional[Any] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
            "result": self.result,
            "error": self.error,
            "message": self.message,
            "task_id": self.task_id,
            "metadata": self.metadata,
            "duration_ms": self.duration_ms
        }
