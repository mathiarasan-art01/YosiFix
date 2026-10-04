"""Initialize and seed the YosiFix database.

Creates all tables, runs migrations, and seeds:
1. Default user accounts:
   - Arasan (arasan@yosifix.dev / password123)
   - admin (admin@yosifix.dev / password123)
   - demo (demo@yosifix.dev / demo123)
   - Google_Test_User (google_demo_user@gmail.com)
2. Complete sample project:
   - "AI-Powered AgroVision: Edge-Device Crop Disease Diagnostic Network"
   - Complete 15-stage analysis pipeline output
   - 8 verified evidence sources (PlantVillage, MobileNetV4, EdgeTPU, arXiv papers)
   - Technical blueprint, architecture diagrams, and judge prep questions
3. Writes database to both instance/yosifix.db and seed_data/yosifix.db for cloud deployments.
"""
import os
import shutil
import json
from datetime import datetime, timezone

from app import create_app
from extensions import db
from migrate_db import upgrade_db
from models import (
    User, Idea, IdeaVersion, PromptRecord,
    AnalysisStage, AnalysisResult, EvidenceSource,
    UserOverride, JudgeAnswer, Notification
)


def seed_database(app=None):
    if app is None:
        app = create_app()

    with app.app_context():
        print("[1/5] Creating database tables...")
        db.create_all()
        upgrade_db()

        print("[2/5] Seeding core user accounts...")
        # 1. Arasan (Main Developer / User)
        arasan = User.query.filter_by(username="Arasan").first()
        if not arasan:
            arasan = User(
                username="Arasan",
                email="arasan@yosifix.dev",
                preferred_language="en"
            )
            arasan.set_password("password123")
            db.session.add(arasan)
            print("  + Created user: Arasan (arasan@yosifix.dev / password123)")
        else:
            arasan.set_password("password123")
            arasan.email = "arasan@yosifix.dev"
            print("  ~ Updated user: Arasan")

        # 2. Admin User
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@yosifix.dev",
                preferred_language="en"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("  + Created user: admin (admin@yosifix.dev / admin123)")
        else:
            admin.set_password("admin123")
            print("  ~ Updated user: admin")

        # 3. Demo User
        demo = User.query.filter_by(username="demo").first()
        if not demo:
            demo = User(
                username="demo",
                email="demo@yosifix.dev",
                preferred_language="en"
            )
            demo.set_password("demo123")
            db.session.add(demo)
            print("  + Created user: demo (demo@yosifix.dev / demo123)")
        else:
            demo.set_password("demo123")
            print("  ~ Updated user: demo")

        # 4. Google Test User
        google_user = User.query.filter_by(google_id="demo_google_1029384756").first()
        if not google_user:
            google_user = User(
                username="Google_Test_User",
                email="google_demo_user@gmail.com",
                password_hash="GOOGLE_OAUTH_USER",
                google_id="demo_google_1029384756",
                avatar_url="https://lh3.googleusercontent.com/a/default-user=s96-c",
                preferred_language="en"
            )
            db.session.add(google_user)
            print("  + Created user: Google_Test_User (google_demo_user@gmail.com)")

        db.session.commit()

        print("[3/5] Seeding flagship project & evidence board...")
        sample_title = "AI-Powered AgroVision: Edge-Device Crop Disease Diagnostic Network"
        sample_idea = Idea.query.filter_by(title=sample_title).first()
        if sample_idea and len(sample_idea.stages) == 0:
            db.session.delete(sample_idea)
            db.session.commit()
            sample_idea = None

        if not sample_idea:
            sample_idea = Idea(
                user_id=arasan.id,
                title=sample_title,
                raw_text=(
                    "An offline-first crop disease diagnostic system deploying lightweight vision "
                    "models (MobileNetV4 + INT8 quantization) on low-cost edge microcontrollers "
                    "(ESP32-CAM / Raspberry Pi Zero 2W). Designed for smallholder farmers in bandwidth-limited "
                    "rural regions with solar harvesting, SMS leaf-stress alerts, and asynchronous peer-to-peer "
                    "federated model updates over LoRa mesh networks."
                ),
                language="en",
                domain="Smart Agriculture & Edge AI",
                domain_confidence=0.96,
                innovation_score=88.5,
                current_version=1,
                status="blueprint",
                selected_mutation_id="MUT-002"
            )
            db.session.add(sample_idea)
            db.session.commit()
            print(f"  + Created sample project: '{sample_title}' (ID: {sample_idea.id})")

            # Project Version 1
            v1 = IdeaVersion(
                idea_id=sample_idea.id,
                version_num=1,
                raw_text=sample_idea.raw_text,
                stage="blueprint",
                actor="user",
                snapshot={"title": sample_idea.title, "domain": sample_idea.domain}
            )
            db.session.add(v1)

            # Prompt Record
            pr = PromptRecord(
                idea_id=sample_idea.id,
                target_tool="groq-llama-3.3-70b-versatile",
                prompt_text=(
                    "Evaluate edge AI crop disease diagnostics under rural bandwidth constraints. "
                    "Evidence-first engineering validation pipeline for deep tech projects."
                )
            )
            db.session.add(pr)

            # 8 Evidence Sources
            evidence_data = [
                ("EV-001", "dataset", "PlantVillage Crop Disease Benchmark Dataset", "https://github.com/spMohanty/PlantVillage-Dataset", "GitHub", "54,306 images of healthy and diseased crops across 14 crop species and 26 diseases.", {"stars": 2400, "citations": 1820}),
                ("EV-002", "paper", "MobileNetV4 — Universal Models for the Mobile Ecosystem", "https://arxiv.org/abs/2404.10518", "arXiv", "Google Research architecture achieving Pareto-optimal latency/accuracy on mobile devices and edge NPUs.", {"citations": 140}),
                ("EV-003", "github", "TensorFlow Lite Micro (TFLM) ESP32 Firmware", "https://github.com/espressif/esp-tflite-micro", "GitHub", "Embedded deep learning inference engine optimized for Xtensa and RISC-V microcontrollers.", {"stars": 1150}),
                ("EV-004", "paper", "LoRaWAN Mesh Networks in Precision Agriculture: Field Trials", "https://doi.org/10.1109/JIOT.2023.3289011", "IEEE IoT Journal", "Real-world packet delivery evaluation under canopy leaf obstruction over 5km radius.", {"citations": 48}),
                ("EV-005", "product", "Seeed Studio Grove Smart Agriculture Kit", "https://www.seeedstudio.com", "Industry Hardware", "Commercial environmental sensors measuring soil moisture, NPK, and ambient humidity.", {}),
                ("EV-006", "dataset", "Cassava Leaf Disease Dataset (Kaggle)", "https://www.kaggle.com/c/cassava-leaf-disease-classification", "Kaggle", "21,367 labeled real-world farmer photos collected in Uganda under uncontrolled lighting.", {"downloads": 15800}),
                ("EV-007", "documentation", "ONNX Runtime Web and Embedded Edge Execution", "https://onnxruntime.ai", "ONNX Docs", "Cross-platform model export pipeline with dynamic INT8 weight quantization.", {}),
                ("EV-008", "paper", "Edge-Computing-Based Early Blight Detection in Solanaceae", "https://doi.org/10.1016/j.compag.2024.108712", "Computers and Electronics in Agriculture", "Empirical study proving 91.4% field accuracy with <120ms latency on Raspberry Pi Zero 2W.", {"citations": 19}),
            ]
            for code, etype, title, url, sname, desc, metrics in evidence_data:
                ev = EvidenceSource(
                    idea_id=sample_idea.id,
                    code=code,
                    type=etype,
                    title=title,
                    url=url,
                    source_name=sname,
                    description=desc,
                    metrics=metrics,
                    relevance=0.92,
                    verification_status="verified"
                )
                db.session.add(ev)

            # 15 Analysis Stages with structured JSON outputs
            stages_content = {
                "extract": {
                    "domain": "Smart Agriculture & Edge AI",
                    "core_entities": ["Vision Transformers", "ESP32-CAM", "PlantVillage", "LoRa", "Solar Harvesting"],
                    "primary_user": "Smallholder farmers and agronomy extension workers in emerging economies",
                    "unresolved_assumptions": ["Lighting variation in direct equatorial sunlight", "Dust accumulation on optical lenses"]
                },
                "evidence": {
                    "sources_analyzed": 8,
                    "coverage_score": 94,
                    "strongest_pillar": "Hardware cost (<$18 total BOM) and offline standalone inference"
                },
                "similarity": {
                    "existing_solutions": [
                        {"name": "Plantix App", "similarity": 0.65, "gap": "Requires 4G cloud connectivity; closed proprietary dataset"},
                        {"name": "FarmPulse Drone Diagnostic", "similarity": 0.42, "gap": "High CAPEX ($2500+); unaffordable for smallholders"}
                    ],
                    "overall_similarity": 48.0,
                    "verdict": "Moderate similarity in vision task, but distinct zero-cloud edge hardware execution."
                },
                "novelty": {
                    "score": 88.5,
                    "breakdown": {
                        "technical": 91,
                        "market_need": 94,
                        "execution_gap": 81
                    },
                    "moat": "Zero-cloud edge inference with decentralized asynchronous federated weight updates over sub-GHz LoRa."
                },
                "research_gaps": {
                    "unaddressed_problems": [
                        "Field lighting fluctuations and wet leaf glare causing false positives in early blight classification",
                        "Ultra-low-power sleep cycles while maintaining periodic leaf anomaly detection"
                    ]
                },
                "mutations": {
                    "options": [
                        {"id": "MUT-001", "name": "Pure Cloud API", "recommendation": "Reject (violates offline constraint)"},
                        {"id": "MUT-002", "name": "Hybrid Edge-LoRa Mesh", "recommendation": "Adopted (highest resilience & lowest TCO)"},
                        {"id": "MUT-003", "name": "Drone Autonomous Flyover", "recommendation": "Deferred to Phase 3"}
                    ]
                },
                "reality_check": {
                    "feasibility_score": 84,
                    "hardware_readiness": "ESP32-CAM ($6.50) + OV2640 sensor are commercially available off the shelf.",
                    "regulatory": "Unlicensed 868/915 MHz ISM band compliant across US, EU, and India."
                },
                "failure_scenarios": {
                    "scenarios": [
                        {"risk": "Lens fungal growth in monsoon season", "mitigation": "Hydrophobic nano-coating lens protector ($0.40/unit)"},
                        {"risk": "Out-of-distribution weed leaves", "mitigation": "Uncertainty thresholding with fallback human-in-the-loop review"}
                    ]
                },
                "sdg": {
                    "primary_goals": [
                        {"sdg": 2, "name": "Zero Hunger", "impact": "Prevents 18-24% annual crop loss from delayed pest detection"},
                        {"sdg": 9, "name": "Industry, Innovation and Infrastructure", "impact": "Brings AI compute directly to disconnected agricultural communities"},
                        {"sdg": 12, "name": "Responsible Consumption & Production", "impact": "Targeted chemical spraying reduces fungicide runoff by 35%"}
                    ]
                },
                "technology": {
                    "edge_stack": ["C++ / ESP-IDF", "TensorFlow Lite Micro", "FreeRTOS", "SX1276 LoRa Driver"],
                    "gateway_stack": ["Python 3.12", "FastAPI", "SQLite / DuckDB", "LoRaWAN Packet Forwarder"],
                    "web_dashboard": ["Flask 3.1", "Bootstrap 5.3", "Mermaid.js", "Chart.js"]
                },
                "requirements": {
                    "functional": ["Trigger image capture every 30 minutes during daylight", "Classify 26 diseases with top-1 accuracy > 88%"],
                    "non_functional": ["Power draw < 15mA in deep sleep", "BOM cost < $20 per sensing node"]
                },
                "architecture": {
                    "diagram_mermaid": "graph TD\n    A[Solar Panel + 18650 LiPo] --> B[ESP32-CAM Node]\n    C[OV2640 Lens] --> B\n    B -->|INT8 TFLM Model| D{Disease Detected?}\n    D -->|Yes| E[SX1276 LoRa Transceiver]\n    D -->|No| F[Deep Sleep 30m]\n    E -->|868MHz Mesh| G[Village Hub Raspberry Pi]\n    G -->|GSM/SMS| H[Farmer Mobile Alert]\n    G -->|Local WiFi| I[YosiFix Offline Dashboard]"
                },
                "roadmap": {
                    "phases": [
                        {"phase": "M1 (Weeks 1-3)", "goal": "INT8 model quantization & ESP32 benchmark (<140ms inference)"},
                        {"phase": "M2 (Weeks 4-6)", "goal": "Solar battery power circuit & outdoor weatherproof IP65 housing"},
                        {"phase": "M3 (Weeks 7-9)", "goal": "LoRa mesh field test across 10 hectares with 5 prototype nodes"},
                        {"phase": "M4 (Weeks 10-12)", "goal": "Agronomist validation trial and farmer dashboard deployment"}
                    ]
                },
                "judge_questions": {
                    "qa_pairs": [
                        {
                            "question": "How do you handle severe sunlight glare when a farmer leaves the node in full sun?",
                            "answer": "We enforce exposure bracketing via the OV2640 register and compute an entropy-based glare mask before feeding the tensor into the quantized MobileNet backbone."
                        },
                        {
                            "question": "Why not use a simple smartphone camera app instead of dedicated edge hardware?",
                            "answer": "Continuous surveillance detects spore symptoms 48 hours before visual wilting, when human scouting is too late. Furthermore, 42% of smallholder farmers do not possess dedicated smartphones in fields."
                        }
                    ]
                },
                "blueprint": {
                    "project_slug": "agrovision-edge-net",
                    "license": "Apache-2.0",
                    "estimated_budget_usd": 1250,
                    "target_trl": "TRL 6 (Demonstration in relevant agricultural environment)",
                    "summary": "Production-ready edge diagnostic pipeline ready for hackathon presentation and grant submission."
                }
            }

            for skey, sdata in stages_content.items():
                stg = AnalysisStage(
                    idea_id=sample_idea.id,
                    stage_key=skey,
                    status="done",
                    output=sdata,
                    engine="groq-llama-3.3-70b-versatile",
                    confidence=92,
                    duration_ms=450,
                    completed_at=datetime.now(timezone.utc)
                )
                db.session.add(stg)

            # Legacy AnalysisResult row
            res = AnalysisResult(
                idea_id=sample_idea.id,
                similar_solutions=stages_content["similarity"]["existing_solutions"],
                overall_similarity=48.0,
                similarity_verdict=stages_content["similarity"]["verdict"],
                covered_features=["Mobile image classification", "Disease symptom visual guide"],
                gap_features=["Autonomous solar-powered surveillance", "LoRa mesh syncing", "Zero-cloud inference"],
                sdg_mappings=stages_content["sdg"]["primary_goals"],
                tech_stack=stages_content["technology"],
                architecture_mermaid=stages_content["architecture"]["diagram_mermaid"]
            )
            db.session.add(res)

            # Notification
            notif = Notification(
                user_id=arasan.id,
                idea_id=sample_idea.id,
                kind="success",
                message="Your edge agricultural diagnostic pipeline has completed all 15 stages with an 88.5% Innovation Score!",
                link=f"/idea/{sample_idea.id}/result"
            )
            db.session.add(notif)
            db.session.commit()
            print("  + Populated all 15 pipeline stages, evidence citations, and blueprint results.")

        print("[4/5] Syncing database to seed_data/yosifix.db for cloud deployments...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        instance_db = os.path.join(base_dir, "instance", "yosifix.db")
        seed_dir = os.path.join(base_dir, "seed_data")
        os.makedirs(seed_dir, exist_ok=True)
        seed_db = os.path.join(seed_dir, "yosifix.db")

        if os.path.exists(instance_db):
            shutil.copy2(instance_db, seed_db)
            print(f"  + Successfully saved seed database: {seed_db} ({os.path.getsize(seed_db)} bytes)")

        print("[5/5] Verification summary:")
        print(f"  - Total Users: {User.query.count()}")
        for u in User.query.all():
            print(f"    * ID {u.id}: {u.username} <{u.email}> (has_password={u.has_password})")
        print(f"  - Total Projects: {Idea.query.count()}")
        for p in Idea.query.all():
            print(f"    * Project #{p.id}: '{p.title}' (stages={len(p.stages)}, evidence={len(p.evidence)})")

        print("\nDatabase initialization complete! Everything is ready for local and cloud use.")


if __name__ == "__main__":
    seed_database()
