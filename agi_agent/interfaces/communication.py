"""
Communication interface for the AGI Agent.
Handles natural language processing and user interaction.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..core.reasoning_engine import ReasoningEngine


@dataclass
class CommunicationContext:
    """Context for communication."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_history: List[Dict[str, str]] = None
    user_preferences: Dict[str, Any] = None


class CommunicationInterface:
    """
    Handles communication between the agent and users.
    """
    
    def __init__(self, reasoning_engine: ReasoningEngine):
        self.reasoning_engine = reasoning_engine
        self.logger = logging.getLogger(__name__)
        
        # Communication templates
        self.response_templates = self._initialize_response_templates()
        
        self.logger.info("Communication interface initialized")
    
    def _initialize_response_templates(self) -> Dict[str, str]:
        """Initialize response templates for different situations."""
        return {
            "task_started": "🔄 I'm working on your task: {task_description}",
            "task_completed": "✅ Task completed successfully! {summary}",
            "task_failed": "❌ I encountered an issue: {error_message}",
            "need_clarification": "🤔 I need some clarification: {question}",
            "safety_approval": "⚠️ This action requires your approval: {action_description}",
            "progress_update": "📊 Progress update: {progress_info}",
            "thinking": "🧠 Let me think about this...",
            "planning": "📋 Creating an execution plan...",
            "learning": "📚 Learning from this experience..."
        }
    
    async def process_user_input(self, user_input: str, context: CommunicationContext = None) -> Dict[str, Any]:
        """
        Process user input and prepare it for the agent.
        
        Args:
            user_input: Raw user input
            context: Communication context
            
        Returns:
            Processed input with metadata
        """
        if context is None:
            context = CommunicationContext()
        
        # Analyze user intent
        intent_analysis = await self._analyze_user_intent(user_input, context)
        
        # Extract task information
        task_info = await self._extract_task_information(user_input, intent_analysis)
        
        # Prepare context for agent
        agent_context = self._prepare_agent_context(context, intent_analysis)
        
        return {
            "processed_input": user_input,
            "intent": intent_analysis,
            "task_info": task_info,
            "context": agent_context,
            "requires_clarification": intent_analysis.get("confidence", 1.0) < 0.7
        }
    
    async def _analyze_user_intent(self, user_input: str, context: CommunicationContext) -> Dict[str, Any]:
        """Analyze user intent from input."""
        prompt = f"""
        Analyze the user's intent from this input:
        
        Input: "{user_input}"
        
        Determine:
        1. Primary intent (task_request, question, clarification, feedback, etc.)
        2. Urgency level (low, medium, high, urgent)
        3. Task type (creative, analytical, problem_solving, informational, etc.)
        4. Confidence level (0.0 to 1.0)
        5. Required capabilities
        
        Respond in JSON format.
        """
        
        response = await self.reasoning_engine._query_model(prompt)
        
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback analysis
            return {
                "primary_intent": "task_request",
                "urgency_level": "medium",
                "task_type": "general",
                "confidence": 0.8,
                "required_capabilities": ["reasoning"]
            }
    
    async def _extract_task_information(self, user_input: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured task information from user input."""
        if intent_analysis.get("primary_intent") != "task_request":
            return {}
        
        prompt = f"""
        Extract task information from this request:
        
        Request: "{user_input}"
        Intent: {intent_analysis.get("task_type", "general")}
        
        Extract:
        1. Main objective
        2. Specific requirements
        3. Constraints or limitations
        4. Expected deliverables
        5. Success criteria
        
        Respond in JSON format.
        """
        
        response = await self.reasoning_engine._query_model(prompt)
        
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "main_objective": user_input,
                "requirements": [],
                "constraints": [],
                "deliverables": ["Task completion"],
                "success_criteria": ["User satisfaction"]
            }
    
    def _prepare_agent_context(self, comm_context: CommunicationContext, 
                             intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for the agent."""
        agent_context = {
            "communication_context": {
                "user_id": comm_context.user_id,
                "session_id": comm_context.session_id,
                "user_preferences": comm_context.user_preferences or {}
            },
            "intent_analysis": intent_analysis
        }
        
        # Add conversation history if available
        if comm_context.conversation_history:
            agent_context["conversation_history"] = comm_context.conversation_history[-5:]  # Last 5 messages
        
        return agent_context
    
    def format_response(self, response_type: str, **kwargs) -> str:
        """Format a response using templates."""
        template = self.response_templates.get(response_type, "{message}")
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.warning(f"Missing template parameter: {e}")
            return kwargs.get("message", "Response formatting error")
    
    def format_task_result(self, result: Dict[str, Any]) -> str:
        """Format task result for user presentation."""
        if not result.get("success", False):
            return self.format_response("task_failed", 
                                      error_message=result.get("error", "Unknown error"))
        
        # Format successful result
        summary_parts = []
        
        if result.get("result"):
            task_result = result["result"]
            if isinstance(task_result, dict):
                if "results" in task_result:
                    summary_parts.append(f"Completed {len(task_result['results'])} steps")
                if "tools_used" in task_result:
                    tools = task_result["tools_used"]
                    if tools:
                        summary_parts.append(f"Used tools: {', '.join(tools)}")
        
        if result.get("metadata"):
            metadata = result["metadata"]
            if "reasoning_steps" in metadata:
                summary_parts.append(f"Applied {metadata['reasoning_steps']} reasoning steps")
        
        summary = ". ".join(summary_parts) if summary_parts else "Task completed"
        
        return self.format_response("task_completed", summary=summary)
    
    def format_progress_update(self, progress: Dict[str, Any]) -> str:
        """Format progress update for user."""
        progress_info = []
        
        if "current_step" in progress:
            progress_info.append(f"Current step: {progress['current_step']}")
        
        if "progress_percentage" in progress:
            progress_info.append(f"Progress: {progress['progress_percentage']:.1f}%")
        
        if "completed_steps" in progress and "total_steps" in progress:
            progress_info.append(f"Steps: {progress['completed_steps']}/{progress['total_steps']}")
        
        info_text = ", ".join(progress_info) if progress_info else "Working on your task"
        
        return self.format_response("progress_update", progress_info=info_text)
    
    def format_clarification_request(self, question: str, options: List[str] = None) -> str:
        """Format a clarification request."""
        formatted_question = question
        
        if options:
            formatted_question += "\n\nOptions:\n"
            for i, option in enumerate(options, 1):
                formatted_question += f"{i}. {option}\n"
        
        return self.format_response("need_clarification", question=formatted_question)
    
    def format_safety_approval_request(self, action: str, risk_info: Dict[str, Any]) -> str:
        """Format a safety approval request."""
        action_description = f"Action: {action}\n"
        
        if risk_info.get("risk_level"):
            action_description += f"Risk Level: {risk_info['risk_level']}\n"
        
        if risk_info.get("reason"):
            action_description += f"Reason: {risk_info['reason']}\n"
        
        if risk_info.get("suggested_modifications"):
            action_description += "\nSuggested modifications:\n"
            for mod in risk_info["suggested_modifications"]:
                action_description += f"• {mod}\n"
        
        action_description += "\nDo you approve this action? (yes/no)"
        
        return self.format_response("safety_approval", action_description=action_description)
    
    async def generate_explanation(self, topic: str, complexity_level: str = "medium") -> str:
        """Generate an explanation for a topic."""
        prompt = f"""
        Explain this topic clearly and concisely:
        
        Topic: {topic}
        Complexity Level: {complexity_level}
        
        Provide an explanation that is:
        - Clear and easy to understand
        - Appropriate for the complexity level
        - Engaging and informative
        - Well-structured
        """
        
        explanation = await self.reasoning_engine._query_model(prompt)
        return explanation
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics."""
        return {
            "available_templates": len(self.response_templates),
            "template_types": list(self.response_templates.keys())
        }
