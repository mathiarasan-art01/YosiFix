"""Generates structured search queries across different research verticals."""
import re
from typing import Dict, List, Any
from services.common.text import keywords, tokenize

def generate_research_queries(context: Dict[str, Any]) -> Dict[str, List[str]]:
    """Derive targeted search queries for GitHub, academic papers, datasets, and commercial products."""
    idea_text = context.get("original_idea", "") or context.get("normalized_idea", "")
    domain = context.get("domain", "")
    problem = context.get("problem", "")
    kw_list = context.get("keywords", []) or keywords(f"{idea_text} {problem}")[:6]

    clean_kw = " ".join(kw_list[:3]) if kw_list else domain
    
    return {
        "github": [
            f"{clean_kw}",
            f"{domain} {kw_list[0]}" if kw_list else domain,
        ],
        "papers": [
            f"{clean_kw}",
            f"{domain} {problem[:50]}" if problem else clean_kw,
        ],
        "datasets": [
            f"{clean_kw}",
            f"{domain} dataset",
        ],
        "products": [
            f"{clean_kw}",
            f"{domain} platform",
        ],
        "web": [
            f"{clean_kw}",
            f"{domain} technology",
        ]
    }
