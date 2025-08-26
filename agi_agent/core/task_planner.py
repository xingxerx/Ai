"""
Task planning system for the AGI Agent.
Decomposes complex tasks into executable plans.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .reasoning_engine import ReasoningEngine, ReasoningType
from ..models.task import Task
from ..models.plan import ExecutionPlan, PlanStep, StepType


class TaskPlanner:
    """
    Task planning system that breaks down complex tasks into executable steps.
    """
    
    def __init__(self, reasoning_engine: ReasoningEngine):
        self.reasoning_engine = reasoning_engine
        self.logger = logging.getLogger(__name__)
        
        # Planning templates for different task types
        self.planning_templates = self._load_planning_templates()
    
    def _load_planning_templates(self) -> Dict[str, str]:
        """Load planning templates for different types of tasks."""
        return {
            "general": """
            Create a detailed execution plan for this task:
            
            Task: {task_description}
            Requirements: {requirements}
            Constraints: {constraints}
            Context: {context}
            
            Break this down into specific, actionable steps. For each step, specify:
            1. Step description
            2. Step type (reasoning, tool_call, decision, validation, synthesis)
            3. Required tools or capabilities
            4. Expected output
            5. Dependencies on other steps
            6. Estimated duration
            
            Respond in JSON format with this structure:
            {{
                "plan_description": "Overall plan description",
                "estimated_duration": "Total estimated time in minutes",
                "steps": [
                    {{
                        "description": "Step description",
                        "step_type": "reasoning|tool_call|decision|validation|synthesis",
                        "tool_name": "tool name if applicable",
                        "parameters": {{}},
                        "expected_output": "What this step should produce",
                        "depends_on": ["step_ids"],
                        "estimated_duration": "time in seconds"
                    }}
                ]
            }}
            """,
            
            "creative": """
            Create an execution plan for this creative task:
            
            Task: {task_description}
            Requirements: {requirements}
            
            Focus on:
            1. Ideation and brainstorming steps
            2. Research and inspiration gathering
            3. Concept development
            4. Iteration and refinement
            5. Final creation and validation
            
            Include creative reasoning steps and synthesis phases.
            Respond in the same JSON format as above.
            """,
            
            "analytical": """
            Create an execution plan for this analytical task:
            
            Task: {task_description}
            Requirements: {requirements}
            Data: {context}
            
            Focus on:
            1. Data gathering and validation
            2. Analysis methodology selection
            3. Step-by-step analysis
            4. Results interpretation
            5. Conclusion and recommendations
            
            Include validation steps and quality checks.
            Respond in the same JSON format as above.
            """,
            
            "problem_solving": """
            Create an execution plan for this problem-solving task:
            
            Task: {task_description}
            Problem: {requirements}
            Constraints: {constraints}
            
            Focus on:
            1. Problem understanding and definition
            2. Root cause analysis
            3. Solution generation
            4. Solution evaluation
            5. Implementation planning
            6. Testing and validation
            
            Include decision points and alternative paths.
            Respond in the same JSON format as above.
            """
        }
    
    async def create_plan(self, task: Task) -> ExecutionPlan:
        """
        Create an execution plan for a task.
        
        Args:
            task: The task to create a plan for
            
        Returns:
            ExecutionPlan with detailed steps
        """
        self.logger.info(f"Creating execution plan for task: {task.id}")
        
        # Determine task type and select appropriate template
        task_type = await self._classify_task(task)
        template = self.planning_templates.get(task_type, self.planning_templates["general"])
        
        # Generate the plan using reasoning engine
        plan_prompt = template.format(
            task_description=task.description,
            requirements=", ".join(task.requirements) if task.requirements else "None specified",
            constraints=", ".join(task.constraints) if task.constraints else "None specified",
            context=json.dumps(task.context, indent=2) if task.context else "{}"
        )
        
        # Use strategic reasoning to create the plan
        reasoning_chain = await self.reasoning_engine.reason_about_problem(
            plan_prompt,
            ReasoningType.STRATEGIC
        )
        
        # Parse the plan from the reasoning result
        plan_data = await self._parse_plan_from_reasoning(reasoning_chain)
        
        # Create execution plan object
        execution_plan = ExecutionPlan(
            task_id=task.id,
            description=plan_data.get("plan_description", f"Execution plan for: {task.description}"),
            estimated_total_duration=plan_data.get("estimated_duration", 0),
            steps=[]
        )
        
        # Create plan steps
        for i, step_data in enumerate(plan_data.get("steps", [])):
            step = PlanStep(
                description=step_data.get("description", f"Step {i+1}"),
                step_type=StepType(step_data.get("step_type", "reasoning")),
                tool_name=step_data.get("tool_name"),
                parameters=step_data.get("parameters", {}),
                expected_output=step_data.get("expected_output"),
                depends_on=step_data.get("depends_on", []),
                estimated_duration=step_data.get("estimated_duration", 60)
            )
            execution_plan.add_step(step)
        
        # Validate and optimize the plan
        await self._validate_plan(execution_plan)
        await self._optimize_plan(execution_plan)
        
        self.logger.info(f"Created execution plan with {len(execution_plan.steps)} steps")
        return execution_plan
    
    async def _classify_task(self, task: Task) -> str:
        """Classify the task to select appropriate planning template."""
        classification_prompt = f"""
        Classify this task into one of these categories:
        - general: Standard task requiring mixed capabilities
        - creative: Creative or inventive task
        - analytical: Data analysis or research task
        - problem_solving: Problem-solving or troubleshooting task
        
        Task: {task.description}
        Requirements: {task.requirements}
        
        Respond with just the category name.
        """
        
        response = await self.reasoning_engine._query_model(classification_prompt)
        classification = response.strip().lower()
        
        if classification in self.planning_templates:
            return classification
        else:
            return "general"
    
    async def _parse_plan_from_reasoning(self, reasoning_chain) -> Dict[str, Any]:
        """Parse execution plan from reasoning chain result."""
        # Get the conclusion from the reasoning chain
        conclusion = reasoning_chain.get_conclusion()
        
        if not conclusion:
            return {"steps": []}
        
        # Try to parse as JSON
        try:
            # Look for JSON in the conclusion
            json_start = conclusion.find('{')
            json_end = conclusion.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = conclusion[json_start:json_end]
                return json.loads(json_str)
        
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse steps from text
        return await self._fallback_parse_plan(conclusion)
    
    async def _fallback_parse_plan(self, text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails."""
        steps = []
        lines = text.split('\n')
        
        current_step = None
        step_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for step indicators
            if (line.startswith(f"{step_counter}.") or 
                line.startswith(f"Step {step_counter}") or
                line.startswith("- ") or
                line.startswith("* ")):
                
                if current_step:
                    steps.append(current_step)
                
                current_step = {
                    "description": line,
                    "step_type": "reasoning",
                    "parameters": {},
                    "expected_output": "Step completion",
                    "depends_on": [],
                    "estimated_duration": 60
                }
                step_counter += 1
        
        if current_step:
            steps.append(current_step)
        
        return {
            "plan_description": "Generated execution plan",
            "estimated_duration": len(steps) * 60,
            "steps": steps
        }
    
    async def _validate_plan(self, plan: ExecutionPlan):
        """Validate the execution plan for consistency and feasibility."""
        # Check for circular dependencies
        self._check_circular_dependencies(plan)
        
        # Validate step dependencies exist
        self._validate_dependencies(plan)
        
        # Check for required tools
        await self._check_tool_availability(plan)
    
    def _check_circular_dependencies(self, plan: ExecutionPlan):
        """Check for circular dependencies in the plan."""
        def has_cycle(step_id: str, visited: set, rec_stack: set) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            step = plan.get_step_by_id(step_id)
            if step:
                for dep_id in step.depends_on:
                    if dep_id not in visited:
                        if has_cycle(dep_id, visited, rec_stack):
                            return True
                    elif dep_id in rec_stack:
                        return True
            
            rec_stack.remove(step_id)
            return False
        
        visited = set()
        for step in plan.steps:
            if step.id not in visited:
                if has_cycle(step.id, visited, set()):
                    raise ValueError(f"Circular dependency detected in plan {plan.id}")
    
    def _validate_dependencies(self, plan: ExecutionPlan):
        """Validate that all step dependencies exist."""
        step_ids = {step.id for step in plan.steps}
        
        for step in plan.steps:
            for dep_id in step.depends_on:
                if dep_id not in step_ids:
                    self.logger.warning(f"Step {step.id} depends on non-existent step {dep_id}")
                    step.depends_on.remove(dep_id)
    
    async def _check_tool_availability(self, plan: ExecutionPlan):
        """Check if required tools are available."""
        # This would integrate with the tool framework
        # For now, just log the required tools
        required_tools = set()
        for step in plan.steps:
            if step.tool_name:
                required_tools.add(step.tool_name)
        
        if required_tools:
            self.logger.info(f"Plan requires tools: {', '.join(required_tools)}")
    
    async def _optimize_plan(self, plan: ExecutionPlan):
        """Optimize the execution plan for efficiency."""
        # Identify steps that can run in parallel
        self._identify_parallel_steps(plan)
        
        # Optimize step ordering
        self._optimize_step_order(plan)
    
    def _identify_parallel_steps(self, plan: ExecutionPlan):
        """Identify steps that can be executed in parallel."""
        # This is a placeholder for parallel execution optimization
        # Would analyze dependencies to find independent steps
        pass
    
    def _optimize_step_order(self, plan: ExecutionPlan):
        """Optimize the order of steps for efficiency."""
        # This is a placeholder for step ordering optimization
        # Would reorder steps to minimize waiting time
        pass
    
    async def adapt_plan(self, plan: ExecutionPlan, feedback: Dict[str, Any]) -> ExecutionPlan:
        """
        Adapt an execution plan based on feedback or changing conditions.
        
        Args:
            plan: The original execution plan
            feedback: Feedback about plan execution
            
        Returns:
            Adapted execution plan
        """
        adaptation_prompt = f"""
        Adapt this execution plan based on the feedback:
        
        Original Plan: {plan.description}
        Current Progress: {plan.get_progress()}
        Feedback: {json.dumps(feedback, indent=2)}
        
        Suggest modifications to improve the plan:
        1. Steps to add, remove, or modify
        2. Dependency changes
        3. Parameter adjustments
        4. Alternative approaches
        
        Respond in JSON format with the adaptations.
        """
        
        response = await self.reasoning_engine._query_model(adaptation_prompt)
        
        # Parse adaptations and apply them
        # This is a simplified implementation
        self.logger.info(f"Plan adaptation suggested: {response}")
        
        return plan  # Return original plan for now
