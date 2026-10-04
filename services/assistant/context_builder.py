"""Assistant Context Builder: summarizes project state for AI assistant queries."""
from typing import Dict, Any, Optional
from services.analysis.context import AnalysisContext


class AssistantContextBuilder:
    """Builds grounded system prompts containing the project's verified evidence and decisions."""

    @staticmethod
    def build_system_context(context: AnalysisContext) -> str:
        ctx_dict = context.to_dict()
        idea_title = ctx_dict.get("normalized_idea") or "Innovation Project"
        domain = ctx_dict.get("domain", "General")
        problem = ctx_dict.get("problem", "Unspecified problem")

        selected_mut = ctx_dict.get("selected_mutation_detail", {})
        mutation_title = selected_mut.get("title", "Standard Architecture")

        tech_stack = ctx_dict.get("technology", {}).get("recommended_stack", {})
        tech_summary = ", ".join([f"{k}: {v}" for k, v in tech_stack.items()]) if isinstance(tech_stack, dict) else str(tech_stack)

        evidence = ctx_dict.get("evidence", {})
        claims_summary = [c.get("claim", "") for c in evidence.get("claims", [])[:3] if isinstance(c, dict)]

        failures = ctx_dict.get("failures", {}).get("failure_modes", [])
        failure_summary = [f.get("scenario_title", "") for f in failures[:2] if isinstance(f, dict)]

        return (
            f"You are the YosiFix Chief Innovation & Architecture Advisor.\n"
            f"You are advising on the project: '{idea_title}' (Domain: {domain}).\n"
            f"Problem Statement: {problem}\n"
            f"Strategic Mutation Selected: {mutation_title}\n"
            f"Key Verified Claims: {'; '.join(claims_summary) if claims_summary else 'None recorded'}\n"
            f"Technology Decisions: {tech_summary or 'In progress'}\n"
            f"Primary Failure Risks: {'; '.join(failure_summary) if failure_summary else 'None identified'}\n\n"
            f"STRICT INSTRUCTIONS:\n"
            f"- Ground all answers strictly in this project's context, data, and selected mutation.\n"
            f"- Do NOT invent disconnected facts or recommend generic advice that contradicts the chosen tech stack.\n"
            f"- Be concise, decisive, and pragmatic."
        )
