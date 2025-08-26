"""
Reasoning-related data models.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ReasoningType(Enum):
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    LOGICAL = "logical"
    CAUSAL = "causal"
    STRATEGIC = "strategic"
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"


@dataclass
class ReasoningStep:
    """Represents a single step in a reasoning process."""
    
    step_number: int
    content: str
    reasoning_type: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Step details
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # 0.0 to 1.0
    
    # Metadata
    duration_ms: Optional[int] = None
    memory_used: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "step_number": self.step_number,
            "content": self.content,
            "reasoning_type": self.reasoning_type,
            "timestamp": self.timestamp.isoformat(),
            "inputs": self.inputs,
            "outputs": self.outputs,
            "confidence": self.confidence,
            "duration_ms": self.duration_ms,
            "memory_used": self.memory_used
        }


@dataclass
class ReasoningChain:
    """Represents a chain of reasoning steps."""
    
    problem: str
    reasoning_type: ReasoningType
    steps: List[ReasoningStep]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    # Chain metadata
    context: Optional[Any] = None
    conclusion: Optional[str] = None
    confidence: float = 1.0
    
    def add_step(self, step: ReasoningStep):
        """Add a step to the reasoning chain."""
        self.steps.append(step)
    
    def get_conclusion(self) -> Optional[str]:
        """Get the conclusion from the last step."""
        if self.conclusion:
            return self.conclusion
        
        if self.steps:
            return self.steps[-1].content
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "problem": self.problem,
            "reasoning_type": self.reasoning_type.value,
            "created_at": self.created_at.isoformat(),
            "steps": [step.to_dict() for step in self.steps],
            "conclusion": self.get_conclusion(),
            "confidence": self.confidence
        }


@dataclass
class ThoughtProcess:
    """Represents a complete thought process with multiple reasoning chains."""
    
    query: str
    chains: List[ReasoningChain]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    # Process metadata
    synthesis: Optional[Dict[str, Any]] = None
    final_answer: Optional[str] = None
    confidence: float = 1.0
    
    def add_chain(self, chain: ReasoningChain):
        """Add a reasoning chain to the thought process."""
        self.chains.append(chain)
    
    def synthesize(self, synthesis_result: Dict[str, Any]):
        """Set the synthesis result."""
        self.synthesis = synthesis_result
        self.final_answer = synthesis_result.get("solution")
        self.confidence = synthesis_result.get("confidence", 1.0) / 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "query": self.query,
            "created_at": self.created_at.isoformat(),
            "chains": [chain.to_dict() for chain in self.chains],
            "synthesis": self.synthesis,
            "final_answer": self.final_answer,
            "confidence": self.confidence
        }
