"""Interactive Project Assistant Service powered by Groq and grounded project context."""
import logging
from typing import Dict, Any, List, Optional
from services.groq.client import GroqClient
from services.analysis.context import AnalysisContext
from services.assistant.context_builder import AssistantContextBuilder
from services.assistant.response_validator import AssistantResponseValidator

logger = logging.getLogger("yosifix.assistant")


class AssistantService:
    """Answers user queries grounded in the active project's analysis state."""

    def __init__(self, groq_client: Optional[GroqClient] = None):
        self.client = groq_client or GroqClient()

    def ask(
        self,
        context: AnalysisContext,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Process user inquiry with full context injection."""
        system_prompt = AssistantContextBuilder.build_system_context(context)
        history = chat_history or []

        # If OpenAI is not configured or in offline mode, provide deterministic contextual response
        if not self.client.is_configured():
            msg_lower = user_message.lower()
            mutation = context.selected_mutation_detail.get("title", "selected strategy")
            domain = context.domain
            tech_stack = context.technology.get("recommended_stack", {})
            failures = context.failures.get("failure_modes", [])
            kill_factor = context.failures.get("kill_factor", "operational failure")

            if "database" in msg_lower or "postgres" in msg_lower or "sql" in msg_lower or ("why" in msg_lower and "recommended" in msg_lower):
                db_choice = tech_stack.get("database", "PostgreSQL") if isinstance(tech_stack, dict) else str(tech_stack)
                reply = (
                    f"For {context.normalized_idea or 'this project'} in the {domain} sector, {db_choice} is recommended "
                    f"because it guarantees transactional integrity for project state while enabling robust indexing."
                )
            elif "risk" in msg_lower or "failure" in msg_lower or "kill" in msg_lower or "threat" in msg_lower or "biggest" in msg_lower:
                top_mit = failures[0].get('mitigation_strategy', 'multi-factor verification') if failures and isinstance(failures[0], dict) else 'strict validation'
                reply = (
                    f"Based on the failure simulation for {context.normalized_idea or 'this project'}, the primary risk is: "
                    f"'{kill_factor}'. Recommended mitigation: {top_mit}."
                )
            else:
                reply = (
                    f"Regarding '{user_message}': For {context.normalized_idea or 'this project'} in {domain} adopting the {mutation} pivot, "
                    f"focus on mitigating '{kill_factor}' and validating core workflow requirements."
                )
            return {
                "response": reply,
                "engine": "rule-based",
            }

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-6:]:  # Keep recent context window
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": user_message})

        try:
            raw_answer = self.client._chat_completion(messages, temperature=0.3)
            sanitized = AssistantResponseValidator.sanitize_response(raw_answer, context.to_dict())
            return {
                "response": sanitized,
                "engine": "openai",
            }
        except Exception as e:
            logger.warning(f"OpenAI assistant chat failed: {e}. Falling back to contextual reply.")
            return {
                "response": (
                    f"Based on your project analysis for '{context.normalized_idea or 'your project'}': your selected pivot '{context.selected_mutation_detail.get('title', 'strategy')}' "
                    f"addresses the core market gap. For '{user_message}', ensure your requirements and failure mitigations are tested first."
                ),
                "engine": "rule-based",
            }
