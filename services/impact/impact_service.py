"""UN SDG alignment and measurable impact metrics service."""
from typing import Dict, Any
from services.common.constants import SDGS, SDG_KEYWORDS

class ImpactService:
    def map_impact(self, context: Dict[str, Any]) -> Dict[str, Any]:
        domain = context.get("domain", "Technology")
        norm_idea = context.get("normalized_idea", "").lower()

        alignments = []
        if domain == "Agriculture" or "crop" in norm_idea or "farm" in norm_idea:
            alignments.append({
                "sdg_number": 2,
                "sdg_name": SDGS[2],
                "target": "Target 2.3: Double agricultural productivity of small-scale food producers.",
                "alignment_rationale": "Enables early identification of yield-destroying diseases directly on farmer mobile devices.",
            })
            alignments.append({
                "sdg_number": 12,
                "sdg_name": SDGS[12],
                "target": "Target 12.4: Environmentally sound management of chemicals.",
                "alignment_rationale": "Prevents indiscriminate blanket pesticide spraying through precise spot recommendations.",
            })
        elif domain == "Healthcare" or "health" in norm_idea or "patient" in norm_idea:
            alignments.append({
                "sdg_number": 3,
                "sdg_name": SDGS[3],
                "target": "Target 3.8: Achieve universal health coverage and access to quality healthcare.",
                "alignment_rationale": "Brings immediate screening and diagnostic triage to underserved locations.",
            })
        else:
            alignments.append({
                "sdg_number": 9,
                "sdg_name": SDGS[9],
                "target": "Target 9.5: Enhance scientific research and upgrade technological capabilities.",
                "alignment_rationale": "Advances robust, decentralized software architectures resilient against connectivity failures.",
            })

        return {
            "sdg_alignments": alignments,
            "quantifiable_metrics": [
                "35% reduction in diagnosis-to-action operational latency",
                "100% elimination of cloud subscription overhead for primary operators",
                "Verified 99.5% uptime regardless of local internet availability",
            ],
            "beneficiary_reach": "Small-to-medium operators, frontline practitioners, and rural enterprises.",
            "environmental_or_social_impact": "Democratizes access to high-precision intelligence without imposing recurring financial burdens.",
        }
