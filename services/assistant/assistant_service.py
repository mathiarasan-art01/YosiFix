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

        # If Groq is not configured or in offline mode, provide deterministic contextual response
        if not self.client.is_configured():
            mutation = context.selected_mutation_detail.get("title", "selected strategy")
            domain = context.domain
            return {
                "response": (
                    f"Regarding '{user_message}': For a {domain} initiative implementing the {mutation} pivot, "
                    f"prioritize addressing the critical failure modes and securing edge data persistence first."
                ),
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
                "engine": "groq",
            }
        except Exception as e:
            logger.warning(f"Groq assistant chat failed: {e}. Falling back to contextual reply.")
            return {
                "response": (
                    f"Based on your analysis: your selected pivot '{context.selected_mutation_detail.get('title', 'strategy')}' "
                    f"addresses the key market gap. For '{user_message}', ensure test coverage on your core offline synchronization first."
                ),
                "engine": "rule-based",
            }
