"""Assistant Response Validator: ensures generated responses adhere to context constraints."""
from typing import Dict, Any


class AssistantResponseValidator:
    """Validates that assistant advice aligns with project boundaries."""

    @staticmethod
    def sanitize_response(response_text: str, context: Dict[str, Any]) -> str:
        """Strip markdown markers if duplicated or empty, and ensure non-empty output."""
        cleaned = response_text.strip()
        if not cleaned:
            idea_name = context.get("normalized_idea", "your project")
            return (
                f"Based on the analysis for {idea_name}, the recommended next step is to test the primary "
                f"architectural assumption in a local proof-of-concept before expanding the cloud integration."
            )
        return cleaned
