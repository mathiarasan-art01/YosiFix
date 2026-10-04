"""Technology stack decision and trade-off justification engine."""
from typing import Dict, Any

class TechnologyService:
    def decide_stack(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "recommended_stack": {
                "Frontend": "Vanilla JS / TypeScript + Bootstrap 5 Glassmorphism UI",
                "Backend": "Python Flask (Microframework with Gunicorn)",
                "Database": "SQLite (Edge / Development) & PostgreSQL (Production Cloud)",
                "AI / ML": "Groq LPU Acceleration + On-Device ONNX Runtime / TF-Lite",
                "Cache & Sync": "In-Memory LRU + Vector Clock Sync",
                "Deployment": "Vercel / Cloud Run Serverless Containers",
            },
            "architecture_pattern": "Offline-First Resilient Edge Architecture",
            "trade_offs": [
                {
                    "layer": "Backend Framework",
                    "selected_tech": "Python Flask",
                    "alternative_considered": "Node.js Express / FastAPI",
                    "reason_selected": "Native seamless integration with scientific AI libraries, TF-IDF, and rapid prototyping without async overhead.",
                    "reason_rejected": "Node.js requires dual-language microservices for native Python machine-learning models.",
                },
                {
                    "layer": "Database",
                    "selected_tech": "SQLite + PostgreSQL Dual Architecture",
                    "alternative_considered": "MongoDB / DynamoDB",
                    "reason_selected": "Single-file zero-config portability locally + ACID relational reliability in production.",
                    "reason_rejected": "NoSQL lacks strict schema enforcement for relational stage dependency graphs.",
                }
            ]
        }
