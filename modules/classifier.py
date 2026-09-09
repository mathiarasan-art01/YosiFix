"""Stage 1: Idea Understanding.

Classifies a raw idea/problem statement into one of the supported
domains using keyword-frequency scoring. Fully deterministic, no
external calls required. If an LLM client is available and configured,
its classification is preferred but the rule-based result is always
computed first as the guaranteed fallback.
"""
import re

DOMAIN_KEYWORDS = {
    "Education": [
        "student", "learn", "school", "college", "teacher", "exam", "study",
        "classroom", "curriculum", "tutor", "quiz", "syllabus", "homework",
        "course", "skill", "training", "literacy", "e-learning", "elearning",
    ],
    "Healthcare": [
        "patient", "doctor", "hospital", "medicine", "health", "diagnosis",
        "clinic", "treatment", "medical", "nurse", "prescription", "symptom",
        "disease", "therapy", "appointment", "telemedicine",
    ],
    "Agriculture": [
        "farmer", "crop", "farming", "soil", "irrigation", "harvest",
        "agriculture", "pesticide", "fertilizer", "livestock", "yield",
        "farm", "seed", "agri",
    ],
    "Environment & Sustainability": [
        "environment", "climate", "carbon", "recycl", "waste", "pollution",
        "sustainab", "renewable", "energy", "biodiversity", "conservation",
        "green", "emission", "plastic",
    ],
    "Fintech & Payments": [
        "payment", "bank", "finance", "loan", "money", "wallet", "budget",
        "invoice", "transaction", "credit", "expense", "insurance", "upi",
        "stock", "invest",
    ],
    "Transportation & Logistics": [
        "transport", "logistics", "delivery", "vehicle", "traffic", "route",
        "fleet", "shipping", "parcel", "ride", "driver", "warehouse",
        "supply chain",
    ],
    "Safety & Security": [
        "safety", "security", "emergency", "crime", "surveillance", "alert",
        "police", "harassment", "danger", "sos", "theft", "disaster",
        "fraud detection", "cyber",
    ],
    "Accessibility & Inclusion": [
        "disab", "accessib", "blind", "deaf", "visually impaired",
        "hearing impaired", "inclusive", "sign language", "wheelchair",
        "assistive",
    ],
    "Productivity & Work": [
        "task", "productivity", "workflow", "team", "project management",
        "collaboration", "meeting", "remote work", "employee", "hr",
        "recruitment", "freelance",
    ],
    "E-commerce & Retail": [
        "shop", "e-commerce", "ecommerce", "retail", "marketplace", "seller",
        "cart", "product listing", "vendor", "inventory", "order",
    ],
    "Mental Health & Wellbeing": [
        "mental health", "stress", "anxiety", "depression", "wellbeing",
        "wellness", "meditation", "mindfulness", "counsel", "therapy session",
        "mood", "burnout",
    ],
    "Governance & Civic Tech": [
        "government", "civic", "citizen", "public service", "policy",
        "municipal", "grievance", "voting", "election", "scheme",
        "certificate", "corporation office",
    ],
    "Food & Nutrition": [
        "food", "nutrition", "diet", "recipe", "restaurant", "meal",
        "hunger", "calorie", "grocery",
    ],
    "Real Estate & Housing": [
        "property", "rent", "housing", "real estate", "apartment", "tenant",
        "landlord", "lease",
    ],
    "Tourism & Travel": [
        "travel", "tourism", "trip", "hotel", "itinerary", "booking",
        "destination", "tourist",
    ],
}


def _score_domain(text, keywords):
    score = 0
    matched = []
    for kw in keywords:
        pattern = r"\b" + re.escape(kw) + r"\w*"
        hits = re.findall(pattern, text, flags=re.IGNORECASE)
        if hits:
            score += len(hits)
            matched.append(kw)
    return score, matched


def classify_idea_rule_based(text):
    text = text or ""
    results = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score, matched = _score_domain(text, keywords)
        if score > 0:
            results.append((domain, score, matched))

    if not results:
        return {
            "domain": "General / Other",
            "confidence": 0.15,
            "matched_keywords": [],
            "engine": "rule-based",
        }

    results.sort(key=lambda r: r[1], reverse=True)
    top_domain, top_score, top_matched = results[0]
    total_score = sum(r[1] for r in results)
    confidence = round(min(0.95, 0.35 + (top_score / total_score) * 0.6), 2) if total_score else 0.3

    return {
        "domain": top_domain,
        "confidence": confidence,
        "matched_keywords": top_matched[:8],
        "engine": "rule-based",
    }


def classify_idea(text, llm_client=None):
    """Returns the rule-based classification, upgraded by an LLM if
    llm_client is provided and reachable. Never raises -- always
    falls back safely."""
    base_result = classify_idea_rule_based(text)

    if llm_client is None or not llm_client.is_available():
        return base_result

    prompt = (
        "Classify the following project idea into exactly one domain from this list: "
        + ", ".join(DOMAIN_KEYWORDS.keys())
        + ". Respond as JSON only: {\"domain\": \"...\", \"confidence\": 0.0-1.0, \"reasoning\": \"...\"}. "
        f"Idea: {text}"
    )
    llm_response = llm_client.ask_json(prompt)
    if llm_response and "domain" in llm_response:
        return {
            "domain": llm_response.get("domain", base_result["domain"]),
            "confidence": float(llm_response.get("confidence", base_result["confidence"])),
            "matched_keywords": base_result["matched_keywords"],
            "reasoning": llm_response.get("reasoning", ""),
            "engine": "llm",
        }
    return base_result
