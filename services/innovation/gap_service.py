"""Research gap mining and market opportunity detection service."""
from typing import Dict, Any

class GapService:
    def discover_gaps(self, context: Dict[str, Any]) -> Dict[str, Any]:
        domain = context.get("domain", "Technology")
        return {
            "unmet_needs": [
                f"Lack of instant diagnostic feedback when disconnected from cellular coverage in {domain.lower()}.",
                "Prohibitive recurring per-seat subscription models that price out grassroots adopters.",
                "Opaque black-box outputs that fail to explain the rationale to non-technical users.",
            ],
            "technical_white_spaces": [
                "Quantized local neural network inference targeting low-power ARM architectures.",
                "Conflict-free replicated data types (CRDT) for multi-peer offline reconciliation.",
            ],
            "market_gaps": [
                f"Underserved tier-2 and tier-3 rural enterprise operations in {domain}.",
                "Community-driven and open-source models with local language support.",
            ],
            "recommended_angles": [
                "Position as the ultra-reliable offline alternative that never experiences cloud downtime.",
                "Emphasize complete ownership of data with zero ongoing cloud telemetry lock-in.",
            ]
        }
