"""Judge attack simulation and interactive defense readiness engine."""
from typing import Dict, Any, List

class JudgeService:
    def generate_questions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        idea_title = context.get("normalized_idea", "this project")
        domain = context.get("domain", "Technology")

        return {
            "overall_pitch_defense_tip": "Focus heavily on why existing incumbents cannot easily copy your edge/offline architecture without rewriting their entire cloud stack.",
            "questions": [
                {
                    "id": "Q1",
                    "category": "Technical Feasibility & Edge Performance",
                    "question": f"How does {idea_title} guarantee acceptable diagnostic inference latency on memory-constrained client devices without overheating or battery drain?",
                    "why_judges_ask": "Judges want to verify if your offline-first claim has been empirically benchmarked or is merely theoretical wishful thinking.",
                    "model_defense_strategy": "Cite 8-bit quantization (INT8) benchmarks, model pruning, and asynchronous worker execution.",
                    "suggested_talking_points": [
                        "We run INT8 quantized models via ONNX Runtime / TF-Lite with sub-50MB memory footprint.",
                        "Inference runs on a dedicated background thread without locking UI threads.",
                        "Empirical benchmarks demonstrate 280ms average execution on standard Android devices.",
                    ]
                },
                {
                    "id": "Q2",
                    "category": "Market Defensibility & Incumbent Threat",
                    "question": f"If an established player in {domain} decides to launch an offline mode tomorrow, what prevents them from wiping out your competitive advantage?",
                    "why_judges_ask": "Tests whether you have structural differentiation or just a transient feature.",
                    "model_defense_strategy": "Explain architectural debt of centralized SaaS platforms and user-centric data sovereignty.",
                    "suggested_talking_points": [
                        "Incumbent business models rely on centralized data harvesting and recurring cloud telemetry subscriptions.",
                        "Retrofitting offline-first CRDT architectures into legacy client-server systems requires a multi-year rewrite.",
                        "Our open architecture builds direct trust and zero vendor lock-in.",
                    ]
                },
                {
                    "id": "Q3",
                    "category": "Data Drift & Real-World Accuracy",
                    "question": "What happens when anomalous real-world inputs deviate from your training distribution?",
                    "why_judges_ask": "Judges probe whether your solution gracefully handles real-world chaos or catastrophically misleads users.",
                    "model_defense_strategy": "Describe out-of-distribution detection, confidence gating, and human-in-the-loop fallback.",
                    "suggested_talking_points": [
                        "We deploy confidence score gating: predictions below 75% trigger an explicit 'Uncertain — re-capture recommended' warning.",
                        "Users are guided with real-time capture quality tips (lighting, angle, distance).",
                    ]
                }
            ]
        }

    def evaluate_defense(self, question: str, user_answer: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate student pitch defense response in real-time."""
        ans = (user_answer or "").strip()
        word_count = len(ans.split())
        
        # Heuristic scoring based on length, specificity, and evidence citations
        score = 50
        strengths = []
        missing = []

        if word_count >= 20:
            score += 20
            strengths.append("Provided detailed, substantive response rather than one-word answer")
        else:
            missing.append("Answer is too brief; needs concrete technical details")

        if any(w in ans.lower() for w in ["benchmark", "percent", "%", "ms", "offline", "quantiz", "crdt", "evidence", "privacy"]):
            score += 15
            strengths.append("Incorporated concrete technical terminology and measurable parameters")
        else:
            missing.append("Include measurable metrics or specific benchmark numbers to persuade technical judges")

        if any(w in ans.lower() for w in ["because", "whereas", "differ", "advantage", "unlike"]):
            score += 10
            strengths.append("Clearly highlighted comparative differentiation against alternatives")
        else:
            missing.append("Contrast directly against incumbent solutions")

        score = min(95, max(45, score))
        verdict = "Strong Defense" if score >= 75 else ("Moderate Defense" if score >= 60 else "Weak Defense")

        return {
            "score": score,
            "verdict": verdict,
            "strengths": strengths or ["Addressed the question promptly"],
            "missing": missing or ["Keep refining delivery cadence"],
            "critique": "Solid technical reasoning. Strengthen the pitch by citing verifiable field pilot metrics.",
            "upgraded_rebuttal": f"While judges rightfully point out this risk, our architecture explicitly incorporates offline edge validation and multi-factor gating, guaranteeing resilient execution where competitors fail.",
        }
