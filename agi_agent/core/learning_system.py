"""
Learning system for the AGI Agent.
Enables the agent to learn from experiences and improve performance.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from .knowledge_manager import KnowledgeManager
from ..models.task import Task
from ..models.plan import ExecutionPlan


@dataclass
class LearningExperience:
    """Represents a learning experience."""
    id: str
    task_description: str
    execution_plan_id: str
    outcome: str  # "success", "failure", "partial"
    lessons_learned: List[str]
    performance_metrics: Dict[str, float]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_description": self.task_description,
            "execution_plan_id": self.execution_plan_id,
            "outcome": self.outcome,
            "lessons_learned": self.lessons_learned,
            "performance_metrics": self.performance_metrics,
            "timestamp": self.timestamp.isoformat()
        }


class LearningSystem:
    """
    Learning system that helps the agent improve through experience.
    """
    
    def __init__(self, knowledge_manager: KnowledgeManager, enabled: bool = True):
        self.knowledge_manager = knowledge_manager
        self.enabled = enabled
        self.experiences: List[LearningExperience] = []
        self.logger = logging.getLogger(__name__)
        
        if not enabled:
            self.logger.info("Learning system disabled")
            return
        
        self.logger.info("Learning system initialized")
    
    async def learn_from_execution(self, task: Task, execution_plan: ExecutionPlan, 
                                 result: Dict[str, Any]) -> Optional[LearningExperience]:
        """
        Learn from a task execution.
        
        Args:
            task: The executed task
            execution_plan: The execution plan used
            result: The execution result
            
        Returns:
            LearningExperience if learning occurred
        """
        if not self.enabled:
            return None
        
        try:
            # Analyze the execution
            analysis = await self._analyze_execution(task, execution_plan, result)
            
            # Extract lessons learned
            lessons = await self._extract_lessons(analysis)
            
            # Calculate performance metrics
            metrics = self._calculate_metrics(execution_plan, result)
            
            # Create learning experience
            experience = LearningExperience(
                id=f"exp_{task.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                task_description=task.description,
                execution_plan_id=execution_plan.id,
                outcome=self._determine_outcome(result),
                lessons_learned=lessons,
                performance_metrics=metrics,
                timestamp=datetime.now()
            )
            
            # Store the experience
            self.experiences.append(experience)
            
            # Update knowledge base with lessons
            await self._update_knowledge_base(experience)
            
            self.logger.info(f"Learned from execution: {len(lessons)} lessons")
            return experience
        
        except Exception as e:
            self.logger.error(f"Error in learning process: {e}")
            return None
    
    async def _analyze_execution(self, task: Task, execution_plan: ExecutionPlan, 
                               result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the execution to identify learning opportunities."""
        analysis = {
            "task_complexity": self._assess_task_complexity(task),
            "plan_effectiveness": self._assess_plan_effectiveness(execution_plan, result),
            "step_performance": self._analyze_step_performance(execution_plan),
            "resource_usage": self._analyze_resource_usage(execution_plan, result),
            "error_patterns": self._identify_error_patterns(execution_plan)
        }
        
        return analysis
    
    async def _extract_lessons(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract actionable lessons from execution analysis."""
        lessons = []
        
        # Plan effectiveness lessons
        if analysis["plan_effectiveness"] < 0.7:
            lessons.append("Consider more detailed planning for similar tasks")
        
        # Step performance lessons
        failed_steps = [step for step in analysis["step_performance"] 
                       if step.get("success", True) == False]
        if failed_steps:
            lessons.append(f"Review and improve handling of {len(failed_steps)} failed step types")
        
        # Resource usage lessons
        if analysis["resource_usage"].get("time_efficiency", 1.0) < 0.8:
            lessons.append("Optimize time allocation for similar tasks")
        
        # Error pattern lessons
        if analysis["error_patterns"]:
            lessons.append("Implement better error handling for common failure modes")
        
        return lessons
    
    def _calculate_metrics(self, execution_plan: ExecutionPlan, result: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance metrics from execution."""
        progress = execution_plan.get_progress()
        
        metrics = {
            "completion_rate": progress["progress_percentage"] / 100.0,
            "success_rate": 1.0 if result.get("success", False) else 0.0,
            "step_efficiency": progress["completed_steps"] / max(progress["total_steps"], 1),
            "error_rate": progress["failed_steps"] / max(progress["total_steps"], 1)
        }
        
        # Time efficiency (if available)
        if execution_plan.actual_total_duration and execution_plan.estimated_total_duration:
            metrics["time_efficiency"] = min(1.0, 
                execution_plan.estimated_total_duration / execution_plan.actual_total_duration)
        
        return metrics
    
    def _determine_outcome(self, result: Dict[str, Any]) -> str:
        """Determine the outcome of task execution."""
        if result.get("success", False):
            return "success"
        elif result.get("results") and len(result["results"]) > 0:
            return "partial"
        else:
            return "failure"
    
    def _assess_task_complexity(self, task: Task) -> float:
        """Assess task complexity (0.0 to 1.0)."""
        complexity = 0.0
        
        # Factor in requirements
        complexity += min(0.3, len(task.requirements) * 0.1)
        
        # Factor in constraints
        complexity += min(0.2, len(task.constraints) * 0.1)
        
        # Factor in description length (proxy for complexity)
        complexity += min(0.3, len(task.description) / 1000)
        
        # Factor in context complexity
        if task.context:
            complexity += min(0.2, len(str(task.context)) / 500)
        
        return min(1.0, complexity)
    
    def _assess_plan_effectiveness(self, execution_plan: ExecutionPlan, result: Dict[str, Any]) -> float:
        """Assess how effective the execution plan was."""
        progress = execution_plan.get_progress()
        
        # Base effectiveness on completion rate
        effectiveness = progress["progress_percentage"] / 100.0
        
        # Adjust for success
        if result.get("success", False):
            effectiveness = min(1.0, effectiveness + 0.2)
        
        # Penalize for failures
        if progress["failed_steps"] > 0:
            effectiveness *= (1.0 - (progress["failed_steps"] / progress["total_steps"]) * 0.5)
        
        return max(0.0, effectiveness)
    
    def _analyze_step_performance(self, execution_plan: ExecutionPlan) -> List[Dict[str, Any]]:
        """Analyze performance of individual steps."""
        step_analysis = []
        
        for step in execution_plan.steps:
            analysis = {
                "step_id": step.id,
                "step_type": step.step_type.value,
                "success": step.status.value == "completed",
                "duration": step.actual_duration,
                "retry_count": step.retry_count
            }
            step_analysis.append(analysis)
        
        return step_analysis
    
    def _analyze_resource_usage(self, execution_plan: ExecutionPlan, result: Dict[str, Any]) -> Dict[str, float]:
        """Analyze resource usage during execution."""
        usage = {}
        
        # Time efficiency
        if execution_plan.actual_total_duration and execution_plan.estimated_total_duration:
            usage["time_efficiency"] = min(1.0,
                execution_plan.estimated_total_duration / execution_plan.actual_total_duration)
        
        # Tool usage efficiency
        tools_used = result.get("tools_used", set())
        if tools_used:
            usage["tool_diversity"] = len(tools_used) / max(len(execution_plan.steps), 1)
        
        return usage
    
    def _identify_error_patterns(self, execution_plan: ExecutionPlan) -> List[str]:
        """Identify common error patterns."""
        patterns = []
        
        failed_steps = [step for step in execution_plan.steps 
                       if step.status.value == "failed"]
        
        if failed_steps:
            # Group by error type
            error_types = {}
            for step in failed_steps:
                if step.error:
                    error_type = step.error.split(':')[0] if ':' in step.error else step.error
                    error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Identify patterns
            for error_type, count in error_types.items():
                if count > 1:
                    patterns.append(f"Recurring {error_type} errors")
        
        return patterns
    
    async def _update_knowledge_base(self, experience: LearningExperience):
        """Update knowledge base with learning experience."""
        # Add lessons as knowledge items
        for lesson in experience.lessons_learned:
            self.knowledge_manager.add_knowledge(
                content=lesson,
                category="lessons_learned",
                tags=["learning", "experience", experience.outcome],
                source="learning_system",
                confidence=0.8
            )
        
        # Add performance insights
        if experience.performance_metrics:
            insight = f"Task performance: {json.dumps(experience.performance_metrics, indent=2)}"
            self.knowledge_manager.add_knowledge(
                content=insight,
                category="performance_metrics",
                tags=["performance", "metrics", experience.outcome],
                source="learning_system",
                confidence=0.9
            )
    
    def get_learning_insights(self, task_type: str = None) -> Dict[str, Any]:
        """Get learning insights for similar tasks."""
        relevant_experiences = self.experiences
        
        if task_type:
            relevant_experiences = [exp for exp in self.experiences 
                                  if task_type.lower() in exp.task_description.lower()]
        
        if not relevant_experiences:
            return {"insights": [], "recommendations": []}
        
        # Aggregate insights
        success_rate = sum(1 for exp in relevant_experiences 
                          if exp.outcome == "success") / len(relevant_experiences)
        
        common_lessons = {}
        for exp in relevant_experiences:
            for lesson in exp.lessons_learned:
                common_lessons[lesson] = common_lessons.get(lesson, 0) + 1
        
        # Sort lessons by frequency
        top_lessons = sorted(common_lessons.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_experiences": len(relevant_experiences),
            "success_rate": success_rate,
            "top_lessons": [lesson for lesson, count in top_lessons],
            "recommendations": self._generate_recommendations(relevant_experiences)
        }
    
    def _generate_recommendations(self, experiences: List[LearningExperience]) -> List[str]:
        """Generate recommendations based on experiences."""
        recommendations = []
        
        if not experiences:
            return recommendations
        
        # Success rate based recommendations
        success_rate = sum(1 for exp in experiences if exp.outcome == "success") / len(experiences)
        
        if success_rate < 0.7:
            recommendations.append("Consider more thorough planning for this type of task")
        
        # Performance based recommendations
        avg_metrics = {}
        for exp in experiences:
            for metric, value in exp.performance_metrics.items():
                avg_metrics[metric] = avg_metrics.get(metric, []) + [value]
        
        for metric, values in avg_metrics.items():
            avg_value = sum(values) / len(values)
            if avg_value < 0.8:
                recommendations.append(f"Focus on improving {metric.replace('_', ' ')}")
        
        return recommendations
