"""Deterministic heuristic similarity scoring across multiple dimensions."""
from typing import Dict, Any, List
from services.common.text import similarity, tokenize

def compute_heuristic_similarity(idea_text: str, competitor_text: str, domain: str) -> Dict[str, Any]:
    """Compute mathematical lexical & semantic overlap between proposed idea and existing solution."""
    score, shared_terms = similarity(idea_text, competitor_text)
    scaled_pct = round(min(95.0, max(10.0, score * 100)), 1)
    
    return {
        "score": scaled_pct,
        "shared_terms": shared_terms,
        "is_high_overlap": scaled_pct >= 65.0,
    }
