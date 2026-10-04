"""Generates evidence-backed explanations for similarity scores."""
from typing import Dict, Any, List

def explain_similarity(idea_title: str, competitor_name: str, shared_terms: List[str], score: float) -> str:
    """Generate clear, human-readable rationale citing concrete overlap points."""
    terms_str = ", ".join(f"'{t}'" for t in shared_terms[:4]) if shared_terms else "domain workflows"
    if score >= 65:
        return f"{idea_title} exhibits substantial workflow overlap with {competitor_name}, specifically around {terms_str}. Differentiation requires structural or architectural pivoting."
    elif score >= 40:
        return f"{idea_title} shares core technical baseline features with {competitor_name} ({terms_str}), but targets a differentiated operating environment or deployment constraint."
    return f"{idea_title} is structurally distant from {competitor_name}. Minimal direct feature collision detected."
