"""Architecture specification and Mermaid.js diagram generator."""
from typing import Dict, Any

class ArchitectureService:
    def generate_architecture(self, context: Dict[str, Any]) -> Dict[str, Any]:
        idea_title = context.get("normalized_idea", "YosiFix App")[:30].replace('"', '')
        diagram = (
            "graph TD\n"
            "    User([👤 User / Edge Device]) -->|Input / Upload| ClientUI[🖥️ Client Web & Edge UI]\n"
            "    ClientUI -->|Local Cache / IndexedDB| EdgeStorage[(💾 Local Offline Store)]\n"
            "    ClientUI -->|Opportunistic Sync / REST| APIGateway[⚡ Flask API Engine]\n"
            "    APIGateway --> Orchestrator[🧠 Analysis & Orchestration Brain]\n"
            "    Orchestrator --> EvidenceService[📚 Multi-Source Evidence Engine]\n"
            "    Orchestrator --> GroqService[⚡ Groq LPU Inference Service]\n"
            "    APIGateway --> DB[(🗄️ Relational Store: SQLite / Postgres)]\n"
            "    style ClientUI fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff\n"
            "    style Orchestrator fill:#1e1b4b,stroke:#8b5cf6,stroke-width:2px,color:#fff\n"
            "    style GroqService fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff\n"
        )

        return {
            "mermaid_diagram": diagram,
            "components": [
                {
                    "name": "Client Web & Edge UI",
                    "role": "Responsive Glassmorphism interface managing inputs, offline state, and visual charts.",
                    "technologies": "Vanilla JavaScript, HTML5, CSS3, Bootstrap 5",
                    "dependencies": ["Local Offline Store", "Flask API Engine"],
                },
                {
                    "name": "Flask API Engine",
                    "role": "State machine enforcing authentication, CSRF, rate-limiting, and validation.",
                    "technologies": "Flask, SQLAlchemy, Pydantic",
                    "dependencies": ["Orchestrator", "Relational Store"],
                },
                {
                    "name": "Groq LPU Inference Service",
                    "role": "High-throughput reasoning, structured claim evaluation, and judge attack synthesis.",
                    "technologies": "Groq Cloud API SDK, gpt-oss-20b",
                    "dependencies": [],
                }
            ],
            "data_flow_description": "Data enters client -> local validation -> encrypted transit -> orchestration pipeline -> evidence grounding -> persistent storage."
        }
