"""Strategic project mutation engine: transforms generic ideas into winning architectures."""
from typing import Dict, Any, List
from services.common.constants import MUTATION_STRATEGIES

class MutationService:
    def generate_mutations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        domain = context.get("domain", "Technology")
        norm_idea = context.get("normalized_idea", "The project")
        
        mutations = [
            {
                "id": "edge_offline",
                "strategy": "offline_first",
                "title": "Offline-First / Edge-AI Architecture",
                "mutation_type": "edge_offline",
                "pitch": "Operate 100% locally on edge devices without requiring cloud connectivity.",
                "rationale": f"Competitors in {domain} are cloud-dependent. Edge execution unlocks rural and latency-critical environments.",
                "key_modifications": [
                    "Embed quantized models (TFLite / ONNX Runtime) directly on the client",
                    "Store local operational data in encrypted SQLite / indexedDB with CRDT sync",
                    "Opportunistic background sync when intermittent network becomes available",
                ],
                "impact_on_novelty": "Converts a standard SaaS application into an edge-native enterprise tool.",
                "selected": True,
            },
            {
                "id": "privacy_first",
                "strategy": "privacy_first",
                "title": "Zero-Knowledge / Privacy-First Pivot",
                "mutation_type": "privacy_first",
                "pitch": "Zero sensitive user data ever leaves the user device in plaintext.",
                "rationale": f"Regulatory compliance (GDPR, HIPAA) and enterprise hesitation in {domain} make data sovereignty a dominant selling point.",
                "key_modifications": [
                    "Client-side encryption with user-owned private keys",
                    "Federated or local inference without telemetry capture",
                    "Auditable open cryptographic verification proofs",
                ],
                "impact_on_novelty": "Directly invalidates incumbent data-harvesting business models.",
                "selected": False,
            },
            {
                "id": "frugal_low_cost",
                "strategy": "low_cost",
                "title": "Frugal Hardware / Low-Cost Mesh",
                "mutation_type": "low_cost",
                "pitch": "Reduce hardware cost by 10x using commodity microcontrollers and peer mesh.",
                "rationale": "High entry barriers prevent widespread grassroots adoption.",
                "key_modifications": [
                    "Target ESP32 / Raspberry Pi Zero compute footprint",
                    "Use peer-to-peer LoRa / Bluetooth mesh instead of expensive cellular gateways",
                    "Ultra-low power sleep states for multi-year battery operation",
                ],
                "impact_on_novelty": "Expands addressable market to underserved smallholders and grassroots users.",
                "selected": False,
            }
        ]
        return mutations
