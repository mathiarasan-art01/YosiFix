"""Main similarity analysis engine combining heuristics and Groq synthesis."""
from typing import Dict, Any
from services.similarity.heuristic_similarity import compute_heuristic_similarity
from services.similarity.similarity_explainer import explain_similarity

class SimilarityService:
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        idea_text = context.get("original_idea", "")
        solutions = context.get("landscape", {}).get("existing_solutions", [])
        closest_name = solutions[0].get("name", "Market Baseline") if solutions else "Market Baseline"
        closest_desc = solutions[0].get("description", "") if solutions else ""

        heuristic = compute_heuristic_similarity(idea_text, f"{closest_name} {closest_desc}", context.get("domain", ""))
        score = heuristic["score"]
        verdict = "High Overlap" if score >= 65 else ("Moderate Overlap" if score >= 40 else "Highly Distinct")

        return {
            "overall_similarity_score": score,
            "similarity_verdict": verdict,
            "closest_competitor": closest_name,
            "explanation": explain_similarity(context.get("normalized_idea", "The idea"), closest_name, heuristic["shared_terms"], score),
            "feature_overlap": [
                {
                    "feature": "Core Workflow Execution",
                    "overlap_percentage": round(score * 1.1, 1) if score * 1.1 <= 100 else 90.0,
                    "matched_with": closest_name,
                    "differentiation_notes": "Incumbents rely on traditional centralized workflows.",
                },
                {
                    "feature": "Edge / Offline Resilience",
                    "overlap_percentage": 15.0,
                    "matched_with": closest_name,
                    "differentiation_notes": "Key white space: existing solutions require continuous cloud connection.",
                }
            ]
        }
