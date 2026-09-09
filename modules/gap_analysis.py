"""Stage 4-5: Gap Detection + Innovation Opportunity Generation.

Aggregates limitations across the top similar solutions, checks
whether the user's own idea text already addresses each limitation,
and turns unaddressed ones into concrete "opportunity" feature
suggestions. Also computes a 0-100 innovation score used across the
app as a discussion-starter, not an objective fact.
"""
import re


def _mentions_concept(idea_text, limitation_text):
    """Very lightweight overlap check: does the idea text already
    contain enough of the limitation's key words to suggest the user
    has already thought about addressing it?"""
    stop = {"the", "a", "an", "of", "for", "to", "in", "on", "and", "or", "not", "is", "with", "no"}
    words = [w for w in re.findall(r"[a-z]+", limitation_text.lower()) if w not in stop and len(w) > 3]
    if not words:
        return False
    idea_lower = idea_text.lower()
    hits = sum(1 for w in words if w in idea_lower)
    return hits / len(words) >= 0.4


def detect_gaps(idea_text, similar_matches):
    covered_features = []
    gap_features = []
    opportunity_notes = []
    seen_limitations = set()

    for match in similar_matches:
        for feat in match.get("key_features", []):
            if feat.lower() in idea_text.lower() and feat not in covered_features:
                covered_features.append(feat)

        for limitation in match.get("limitations", []):
            key = limitation.strip().lower()
            if key in seen_limitations:
                continue
            seen_limitations.add(key)

            if _mentions_concept(idea_text, limitation):
                continue  # user's idea already seems to address this

            gap_features.append(limitation)
            opportunity_notes.append(
                f"None of the closely-matched solutions fully solve: \"{limitation}\" "
                f"(gap observed in {match['name']}). Addressing this could be a genuine differentiator."
            )

    if not gap_features:
        opportunity_notes.append(
            "The idea already appears to address the main limitations found in similar solutions — "
            "focus your differentiation on execution quality, UX, and localization instead."
        )

    return {
        "covered_features": covered_features,
        "gap_features": gap_features[:6],
        "opportunity_notes": opportunity_notes[:6],
    }


def compute_innovation_score(overall_similarity, gap_count, sdg_count):
    """0-100 heuristic score: lower market overlap + more addressed
    gaps + broader real-world (SDG) relevance = higher score.
    This is a discussion-starting heuristic, not an objective metric."""
    novelty_component = max(0, 100 - overall_similarity)  # 0-100
    gap_component = min(gap_count, 5) * 8  # up to 40
    sdg_component = min(sdg_count, 3) * 6  # up to 18

    score = 0.5 * novelty_component + 0.3 * (gap_component / 40 * 100) + 0.2 * (sdg_component / 18 * 100)
    return round(min(100, max(5, score)), 1)
