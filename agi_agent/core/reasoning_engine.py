"""
Core reasoning engine for the AGI Agent.
Handles understanding, analysis, and decision-making.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import openai
import anthropic

from ..models.reasoning import ReasoningStep, ReasoningChain, ThoughtProcess
from ..models.task import Task
from .custom_model import CustomModelProvider


class ReasoningType(Enum):
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    LOGICAL = "logical"
    CAUSAL = "causal"
    STRATEGIC = "strategic"


@dataclass
class ReasoningContext:
    """Context for reasoning operations."""
    task: Optional[Task] = None
    previous_steps: List[ReasoningStep] = None
    available_tools: List[str] = None
    constraints: List[str] = None
    knowledge_base: Dict[str, Any] = None


class ReasoningEngine:
    """
    Core reasoning engine that provides various types of reasoning capabilities.
    """
    
    def __init__(self, model_provider: str = "openai", model_name: str = "gpt-4", max_depth: int = 10):
        self.model_provider = model_provider
        self.model_name = model_name
        self.max_depth = max_depth
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI model client
        self._initialize_model()
        
        # Reasoning templates
        self.reasoning_templates = self._load_reasoning_templates()
    
    def _initialize_model(self):
        """Initialize the AI model client."""
        if self.model_provider == "openai":
            self.client = openai.AsyncOpenAI()
        elif self.model_provider == "anthropic":
            self.client = anthropic.AsyncAnthropic()
        elif self.model_provider == "custom":
            # Initialize custom model provider
            self.client = CustomModelProvider(model_name=self.model_name)
            self.logger.info(f"Using custom model provider: {self.model_name}")
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def _load_reasoning_templates(self) -> Dict[str, str]:
        """Load reasoning templates for different types of thinking."""
        return {
            "analytical": """
            Analyze the given problem step by step:
            1. Break down the problem into components
            2. Identify key variables and relationships
            3. Consider multiple perspectives
            4. Evaluate evidence and data
            5. Draw logical conclusions
            
            Problem: {problem}
            Context: {context}
            """,
            
            "creative": """
            Think creatively about this challenge:
            1. Generate multiple novel approaches
            2. Consider unconventional solutions
            3. Combine ideas from different domains
            4. Think beyond obvious constraints
            5. Propose innovative alternatives
            
            Challenge: {problem}
            Context: {context}
            """,
            
            "strategic": """
            Develop a strategic approach:
            1. Define clear objectives
            2. Analyze current situation
            3. Identify opportunities and threats
            4. Consider resource requirements
            5. Plan implementation steps
            
            Goal: {problem}
            Context: {context}
            """,
            
            "causal": """
            Analyze cause and effect relationships:
            1. Identify potential causes
            2. Trace causal chains
            3. Consider feedback loops
            4. Evaluate intervention points
            5. Predict outcomes
            
            Situation: {problem}
            Context: {context}
            """
        }
    
    async def understand_request(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Understand and parse a user request.
        
        Args:
            user_input: The user's request
            context: Additional context information
            
        Returns:
            Dictionary containing parsed understanding
        """
        prompt = f"""
        Analyze this user request and extract key information:
        
        Request: "{user_input}"
        Context: {json.dumps(context, indent=2)}
        
        Please provide a structured analysis including:
        1. Main objective/goal
        2. Required capabilities or tools
        3. Constraints and limitations
        4. Success criteria
        5. Priority level (low/medium/high/urgent)
        6. Estimated complexity (simple/moderate/complex/very_complex)
        7. Required reasoning types (analytical, creative, logical, etc.)
        
        Respond in JSON format.
        """
        
        response = await self._query_model(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            return self._fallback_parse_understanding(user_input, response)
    
    async def reason_about_problem(
        self, 
        problem: str, 
        reasoning_type: ReasoningType,
        context: ReasoningContext = None
    ) -> ReasoningChain:
        """
        Apply specific type of reasoning to a problem.
        
        Args:
            problem: The problem to reason about
            reasoning_type: Type of reasoning to apply
            context: Additional context for reasoning
            
        Returns:
            ReasoningChain containing the thought process
        """
        if context is None:
            context = ReasoningContext()
        
        template = self.reasoning_templates.get(reasoning_type.value, self.reasoning_templates["analytical"])
        
        prompt = template.format(
            problem=problem,
            context=self._format_context(context)
        )
        
        # Add chain-of-thought prompting
        prompt += "\n\nThink through this step by step, showing your reasoning process."
        
        response = await self._query_model(prompt)
        
        # Parse the reasoning steps
        steps = self._parse_reasoning_steps(response)
        
        return ReasoningChain(
            problem=problem,
            reasoning_type=reasoning_type,
            steps=steps,
            context=context
        )
    
    async def execute_reasoning_step(self, step) -> Dict[str, Any]:
        """Execute a reasoning-based step (no external tools)."""
        prompt = f"""
        Execute this reasoning step:
        
        Step: {step.description}
        Parameters: {step.parameters}
        
        Provide the result of this reasoning step.
        """
        
        result = await self._query_model(prompt)
        
        return {
            "step_id": step.id,
            "result": result,
            "type": "reasoning",
            "success": True
        }
    
    async def synthesize_solutions(self, reasoning_chains: List[ReasoningChain]) -> Dict[str, Any]:
        """
        Synthesize multiple reasoning chains into a unified solution.
        
        Args:
            reasoning_chains: List of reasoning chains to synthesize
            
        Returns:
            Synthesized solution
        """
        chains_summary = []
        for chain in reasoning_chains:
            chains_summary.append({
                "type": chain.reasoning_type.value,
                "conclusion": chain.steps[-1].content if chain.steps else "No conclusion",
                "key_insights": [step.content for step in chain.steps[:3]]  # First 3 steps
            })
        
        prompt = f"""
        Synthesize these different reasoning approaches into a unified solution:
        
        {json.dumps(chains_summary, indent=2)}
        
        Provide:
        1. Integrated solution that combines the best insights
        2. Confidence level (0-100%)
        3. Potential risks or limitations
        4. Recommended next steps
        
        Respond in JSON format.
        """
        
        response = await self._query_model(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "solution": response,
                "confidence": 70,
                "risks": ["Unable to parse structured response"],
                "next_steps": ["Review and refine solution"]
            }
    
    async def _query_model(self, prompt: str) -> str:
        """Query the AI model with a prompt."""
        try:
            if self.model_provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                return response.choices[0].message.content

            elif self.model_provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model_name,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            elif self.model_provider == "custom":
                # Use custom model provider
                response = await self.client.generate_response(prompt, temperature=0.7)
                return response

        except Exception as e:
            self.logger.error(f"Error querying model: {e}")
            return f"Error: Unable to process request - {str(e)}"
    
    def _format_context(self, context: ReasoningContext) -> str:
        """Format reasoning context for prompts."""
        context_parts = []
        
        if context.task:
            context_parts.append(f"Task: {context.task.description}")
        
        if context.available_tools:
            context_parts.append(f"Available tools: {', '.join(context.available_tools)}")
        
        if context.constraints:
            context_parts.append(f"Constraints: {', '.join(context.constraints)}")
        
        if context.previous_steps:
            context_parts.append(f"Previous steps: {len(context.previous_steps)} completed")
        
        return "\n".join(context_parts) if context_parts else "No additional context"
    
    def _parse_reasoning_steps(self, response: str) -> List[ReasoningStep]:
        """Parse reasoning steps from model response."""
        steps = []
        lines = response.split('\n')
        
        current_step = None
        step_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for numbered steps or bullet points
            if (line.startswith(f"{step_counter}.") or 
                line.startswith(f"Step {step_counter}") or
                line.startswith("- ") or
                line.startswith("* ")):
                
                if current_step:
                    steps.append(current_step)
                
                current_step = ReasoningStep(
                    step_number=step_counter,
                    content=line,
                    reasoning_type="analytical"
                )
                step_counter += 1
            
            elif current_step:
                # Continue previous step
                current_step.content += " " + line
        
        if current_step:
            steps.append(current_step)
        
        return steps
    
    def _fallback_parse_understanding(self, user_input: str, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails."""
        return {
            "objective": user_input,
            "requirements": ["Natural language processing"],
            "constraints": [],
            "priority": "medium",
            "complexity": "moderate",
            "reasoning_types": ["analytical"],
            "raw_response": response
        }
