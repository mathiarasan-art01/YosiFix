"""Stage 6: SDG Mapping.

Rule-based keyword engine mapping idea text to the 17 UN Sustainable
Development Goals. Deterministic and offline; an LLM can be layered on
top later for nuanced reasoning, but the app never depends on it.
"""
import re

SDGS = {
    1: {"name": "No Poverty", "keywords": ["poverty", "income", "livelihood", "low-income", "poor", "financial inclusion"]},
    2: {"name": "Zero Hunger", "keywords": ["hunger", "food security", "malnutrition", "nutrition", "farming", "crop", "agriculture"]},
    3: {"name": "Good Health and Well-being", "keywords": ["health", "medical", "disease", "hospital", "mental health", "wellbeing", "wellness", "fitness"]},
    4: {"name": "Quality Education", "keywords": ["education", "school", "learning", "student", "literacy", "teacher", "skill training"]},
    5: {"name": "Gender Equality", "keywords": ["women", "gender", "girls", "female safety", "equality"]},
    6: {"name": "Clean Water and Sanitation", "keywords": ["water", "sanitation", "hygiene", "clean water", "sewage", "toilet"]},
    7: {"name": "Affordable and Clean Energy", "keywords": ["energy", "electricity", "solar", "renewable", "power grid"]},
    8: {"name": "Decent Work and Economic Growth", "keywords": ["employment", "job", "work", "economic growth", "entrepreneur", "freelance", "labor"]},
    9: {"name": "Industry, Innovation and Infrastructure", "keywords": ["infrastructure", "innovation", "industry", "manufacturing", "technology access"]},
    10: {"name": "Reduced Inequality", "keywords": ["inequality", "inclusion", "marginalized", "underserved", "accessibility", "disab"]},
    11: {"name": "Sustainable Cities and Communities", "keywords": ["city", "urban", "housing", "traffic", "public transport", "community", "smart city"]},
    12: {"name": "Responsible Consumption and Production", "keywords": ["waste", "recycl", "consumption", "sustainable production", "circular economy"]},
    13: {"name": "Climate Action", "keywords": ["climate", "carbon", "emission", "global warming", "climate change"]},
    14: {"name": "Life Below Water", "keywords": ["ocean", "marine", "fish", "water pollution", "coastal"]},
    15: {"name": "Life on Land", "keywords": ["forest", "biodiversity", "wildlife", "land degradation", "deforestation", "conservation"]},
    16: {"name": "Peace, Justice and Strong Institutions", "keywords": ["justice", "corruption", "governance", "crime", "legal aid", "policy", "civic"]},
    17: {"name": "Partnerships for the Goals", "keywords": ["partnership", "collaboration", "ngo", "government scheme", "cross-sector"]},
}


def map_sdgs(idea_text, top_n=5):
    idea_lower = idea_text.lower()
    results = []

    for number, data in SDGS.items():
        matched = [kw for kw in data["keywords"] if re.search(re.escape(kw), idea_lower)]
        if matched:
            relevance = round(min(1.0, 0.4 + 0.15 * len(matched)), 2)
            results.append({
                "sdg_number": number,
                "sdg_name": data["name"],
                "relevance_score": relevance,
                "matched_keywords": matched,
                "reasoning": f"Idea text references {', '.join(matched[:3])}, aligning with SDG {number}: {data['name']}.",
            })

    results.sort(key=lambda r: r["relevance_score"], reverse=True)
    return results[:top_n]
