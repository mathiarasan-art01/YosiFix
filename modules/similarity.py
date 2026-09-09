"""Stage 3: Similarity Analysis.

Compares the user's idea text against every known solution in the
idea's domain using TF-IDF + cosine similarity (scikit-learn), then
attaches a plain-language reasoning sentence per match. Deterministic
and fully offline -- no external API required.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from modules.knowledge_base import get_domain_entries


def _solution_text(entry):
    return f"{entry['name']}. {entry['description']} " + " ".join(entry.get("key_features", []))


def _reasoning(idea_text, entry, score):
    idea_lower = idea_text.lower()
    shared = [f for f in entry.get("key_features", []) if any(w in idea_lower for w in f.lower().split())]
    if score >= 0.55:
        base = f"Strong overlap with {entry['name']} — both address a very similar core need."
    elif score >= 0.30:
        base = f"Moderate overlap with {entry['name']} — some shared ground, but room to differentiate."
    else:
        base = f"Low overlap with {entry['name']} — your framing appears meaningfully different."
    if shared:
        base += f" Shared themes: {', '.join(shared[:2])}."
    if entry.get("limitations"):
        base += f" Known gap in {entry['name']}: {entry['limitations'][0]}."
    return base


def analyze_similarity(idea_text, domain, top_n=5):
    entries = get_domain_entries(domain)
    if not entries:
        return {
            "matches": [],
            "overall_similarity": 0.0,
            "verdict": "No existing-solution data available for this domain yet — treat this as an open, under-explored space.",
        }

    corpus = [idea_text] + [_solution_text(e) for e in entries]
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    except ValueError:
        # empty vocabulary (e.g. idea text too short / all stopwords)
        sims = [0.0] * len(entries)

    scored = list(zip(entries, sims))
    scored.sort(key=lambda x: x[1], reverse=True)
    scored = scored[:top_n]

    matches = []
    for entry, score in scored:
        matches.append({
            "name": entry["name"],
            "description": entry["description"],
            "key_features": entry.get("key_features", []),
            "limitations": entry.get("limitations", []),
            "similarity_score": round(float(score) * 100, 1),
            "reasoning": _reasoning(idea_text, entry, float(score)),
        })

    overall = matches[0]["similarity_score"] if matches else 0.0
    if overall >= 55:
        verdict = "High overlap with existing solutions — you'll need a sharp, explicit differentiator to stand out."
    elif overall >= 30:
        verdict = "Moderate overlap — a real niche or feature gap exists for you to own."
    else:
        verdict = "Low overlap — this looks like a comparatively novel angle in this space."

    return {
        "matches": matches,
        "overall_similarity": overall,
        "verdict": verdict,
    }
