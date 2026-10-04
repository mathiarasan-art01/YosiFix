"""Novelty scoring and defensibility evaluation service."""
from typing import Dict, Any

class NoveltyService:
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        sim_score = context.get("similarity", {}).get("overall_similarity_score", 50.0)
        # Novelty is inversely proportional to similarity, plus mutation boost
        base_novelty = max(20.0, min(95.0, 100.0 - sim_score + 15.0))
        tier = "Highly Novel" if base_novelty >= 70 else ("Incremental Improvement" if base_novelty >= 45 else "Derivative")

        return {
            "novelty_score": round(base_novelty, 1),
            "novelty_tier": tier,
            "unique_value_props": [
                "Unassisted offline execution capability on standard commodity hardware",
                "Direct peer-to-peer data synchronization eliminating cloud single points of failure",
                "Grounded explainability and evidence-backed decision audits",
            ],
            "novelty_breakdown": {
                "technical_architecture": 82.0,
                "workflow_innovation": 74.0,
                "market_positioning": 80.0,
            },
            "novelty_rationale": "By bypassing centralized SaaS infrastructure and executing locally, the project occupies a defensible white space against cloud incumbents.",
        }
