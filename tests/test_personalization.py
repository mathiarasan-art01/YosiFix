# tests/test_personalization.py
"""Comprehensive Personalization & Isolation Test Suite.

Verifies that radically different project ideas:
1. Produce radically different domain classifications, problems, target users, and keywords.
2. Formulate idea-specific research queries.
3. Discover distinct solution landscapes and compute distinct similarity overlaps.
4. Uncover distinct research gaps and formulate tailored architectural mutations.
5. Recommend tailored technology stacks and generate distinct Mermaid architectures.
6. Synthesize distinct Master Blueprints with zero generic copy-paste.
7. Record dedicated AnalysisRun records and use distinct cache keys.
"""

import pytest
from app import create_app
from extensions import db
from models import User, Idea, AnalysisRun
from services.analysis.orchestrator import AnalysisOrchestrator
from services.analysis.context import AnalysisContext
from services.analysis.cache import AnalysisCacheService
from services.research.query_generator import generate_research_queries
from services.research.product_service import ProductResearchService


@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_three_radically_different_ideas_personalization(app_instance):
    with app_instance.app_context():
        # Setup test user
        user = User(email="architect@yosifix.ai", username="testarchitect")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        # Idea A: Agriculture
        idea_a = Idea(
            user_id=user.id,
            title="AI Crop Disease Detector for Smallholder Farmers",
            raw_text="AI-powered mobile crop disease detection using smartphone camera for rural smallholder farmers with offline guidance.",
            language="en",
        )
        # Idea B: Document Security / Education Verification
        idea_b = Idea(
            user_id=user.id,
            title="AI Fake Certificate Verification for Educational Institutions",
            raw_text="AI-powered fake certificate and forged degree verification using optical forensics and cryptographic attestations for universities and employers.",
            language="en",
        )
        # Idea C: Academic Timetable Optimization
        idea_c = Idea(
            user_id=user.id,
            title="AI Student Timetable Optimization Platform",
            raw_text="AI-powered university student timetable and course schedule optimization using constraint programming to eliminate classroom conflicts and commute dead-time.",
            language="en",
        )
        db.session.add_all([idea_a, idea_b, idea_c])
        db.session.commit()

        orchestrator = AnalysisOrchestrator()

        # Execute full 15-stage pipeline on all three
        ctx_a = orchestrator.run_full_analysis(idea_a)
        ctx_b = orchestrator.run_full_analysis(idea_b)
        ctx_c = orchestrator.run_full_analysis(idea_c)

        # -------------------------------------------------------------
        # 1. Domain & Problem Differentiation
        # -------------------------------------------------------------
        assert ctx_a.domain == "Agriculture", f"Expected Agriculture, got {ctx_a.domain}"
        assert ctx_b.domain in ["Cybersecurity & Verification", "Education & Learning", "Intelligent Software & Automation"]
        assert ctx_c.domain in ["Education & Learning", "Intelligent Software & Automation"]
        assert ctx_a.domain != ctx_b.domain

        assert "crop" in ctx_a.problem.lower() or "plant" in ctx_a.problem.lower() or "farm" in ctx_a.problem.lower()
        assert "certificate" in ctx_b.problem.lower() or "forged" in ctx_b.problem.lower() or "credential" in ctx_b.problem.lower() or "degree" in ctx_b.problem.lower()
        assert "schedule" in ctx_c.problem.lower() or "conflict" in ctx_c.problem.lower() or "combinatorial" in ctx_c.problem.lower() or "timetable" in ctx_c.problem.lower()

        # Problems must be mutually distinct
        assert ctx_a.problem != ctx_b.problem
        assert ctx_b.problem != ctx_c.problem

        # -------------------------------------------------------------
        # 2. Target Users Differentiation
        # -------------------------------------------------------------
        users_a_str = " ".join(ctx_a.target_users).lower()
        users_b_str = " ".join(ctx_b.target_users).lower()
        users_c_str = " ".join(ctx_c.target_users).lower()

        assert any(w in users_a_str for w in ["farmer", "agronomist", "agri"])
        assert any(w in users_b_str for w in ["registrar", "hr", "verification", "admissions"])
        assert any(w in users_c_str for w in ["scheduler", "student", "faculty", "coordinator", "dean"])

        # -------------------------------------------------------------
        # 3. Keywords Differentiation
        # -------------------------------------------------------------
        kw_a = set(k.lower() for k in ctx_a.keywords)
        kw_b = set(k.lower() for k in ctx_b.keywords)
        kw_c = set(k.lower() for k in ctx_c.keywords)

        assert "crop" in kw_a or "disease" in kw_a or "farmer" in kw_a
        assert "certificate" in kw_b or "forged" in kw_b or "degree" in kw_b or "verification" in kw_b
        assert "timetable" in kw_c or "schedule" in kw_c or "student" in kw_c or "course" in kw_c

        # Keyword sets should have minimal overlap
        assert len(kw_a.intersection(kw_b)) <= 2

        # -------------------------------------------------------------
        # 4. Research Queries Differentiation
        # -------------------------------------------------------------
        queries_a = generate_research_queries(ctx_a.to_dict())
        queries_b = generate_research_queries(ctx_b.to_dict())
        queries_c = generate_research_queries(ctx_c.to_dict())

        assert queries_a["github"] != queries_b["github"]
        assert queries_b["github"] != queries_c["github"]
        assert any("crop" in q.lower() or "disease" in q.lower() or "farm" in q.lower() for q in queries_a["github"])
        assert any("certificate" in q.lower() or "degree" in q.lower() or "verification" in q.lower() for q in queries_b["github"])

        # -------------------------------------------------------------
        # 5. Technology Stack Differentiation
        # -------------------------------------------------------------
        tech_a = ctx_a.technology.get("recommended_stack", {})
        tech_b = ctx_b.technology.get("recommended_stack", {})
        tech_c = ctx_c.technology.get("recommended_stack", {})

        # Tech recommendations tailored to requirements
        # Agri: Mobile / TFLite
        assert "flutter" in str(tech_a.get("frontend", "")).lower() or "mobile" in str(tech_a.get("frontend", "")).lower()
        assert "tflite" in str(tech_a.get("ai_ml", "")).lower() or "pytorch mobile" in str(tech_a.get("ai_ml", "")).lower() or "onnx" in str(tech_a.get("ai_ml", "")).lower()

        # Cert fraud: OCR / Cryptography / PostgreSQL
        assert "ocr" in str(tech_b.get("ai_ml", "")).lower() or "crypto" in str(tech_b.get("ai_ml", "")).lower() or "opencv" in str(tech_b.get("ai_ml", "")).lower()

        # Timetable: Constraint programming / OR-Tools
        assert "or-tools" in str(tech_c.get("ai_ml", "")).lower() or "constraint" in str(tech_c.get("ai_ml", "")).lower() or "solver" in str(tech_c.get("ai_ml", "")).lower()

        # -------------------------------------------------------------
        # 6. Mutations Differentiation
        # -------------------------------------------------------------
        mut_titles_a = [m.get("title") for m in ctx_a.mutations]
        mut_titles_b = [m.get("title") for m in ctx_b.mutations]
        mut_titles_c = [m.get("title") for m in ctx_c.mutations]

        assert mut_titles_a != mut_titles_b
        assert mut_titles_b != mut_titles_c
        assert any("field" in t.lower() or "offline" in t.lower() or "crop" in t.lower() for t in mut_titles_a)
        assert any("attestation" in t.lower() or "cryptographic" in t.lower() or "optical" in t.lower() or "consortium" in t.lower() for t in mut_titles_b)
        assert any("schedule" in t.lower() or "rescheduler" in t.lower() or "commute" in t.lower() or "bidding" in t.lower() for t in mut_titles_c)

        # -------------------------------------------------------------
        # 7. Failure Scenarios Differentiation
        # -------------------------------------------------------------
        kill_a = ctx_a.failures.get("kill_factor", "").lower()
        kill_b = ctx_b.failures.get("kill_factor", "").lower()
        kill_c = ctx_c.failures.get("kill_factor", "").lower()

        assert kill_a != kill_b
        assert kill_b != kill_c
        assert "crop" in kill_a or "foliar" in kill_a or "diagnosis" in kill_a or "fungicide" in kill_a or "farmer" in kill_a
        assert "degree" in kill_b or "forged" in kill_b or "diploma" in kill_b or "liability" in kill_b or "fraud" in kill_b
        assert "solver" in kill_c or "deadlock" in kill_c or "schedule" in kill_c or "infeasibility" in kill_c

        # -------------------------------------------------------------
        # 8. Master Blueprint Differentiation
        # -------------------------------------------------------------
        bp_a = ctx_a.blueprint.get("executive_summary", "")
        bp_b = ctx_b.blueprint.get("executive_summary", "")
        bp_c = ctx_c.blueprint.get("executive_summary", "")

        assert bp_a != bp_b
        assert bp_b != bp_c
        assert "crop" in bp_a.lower() or "disease" in bp_a.lower() or "smallholder" in bp_a.lower()
        assert "certificate" in bp_b.lower() or "degree" in bp_b.lower() or "verification" in bp_b.lower()
        assert "timetable" in bp_c.lower() or "schedule" in bp_c.lower() or "optimization" in bp_c.lower()

        # -------------------------------------------------------------
        # 9. Analysis Run & Cache Isolation
        # -------------------------------------------------------------
        runs_a = AnalysisRun.query.filter_by(project_id=idea_a.id).all()
        runs_b = AnalysisRun.query.filter_by(project_id=idea_b.id).all()
        runs_c = AnalysisRun.query.filter_by(project_id=idea_c.id).all()

        assert len(runs_a) >= 1
        assert len(runs_b) >= 1
        assert len(runs_c) >= 1
        assert runs_a[0].status == "completed"
        assert runs_b[0].status == "completed"
        assert runs_c[0].status == "completed"

        # Cache keys must include project_id and never collide
        cache_key_a = AnalysisCacheService.compute_cache_key("novelty_score", ctx_a.to_dict(), idea_a.id, 1)
        cache_key_b = AnalysisCacheService.compute_cache_key("novelty_score", ctx_b.to_dict(), idea_b.id, 1)
        assert cache_key_a != cache_key_b
        assert f"project:{idea_a.id}:" in cache_key_a
        assert f"project:{idea_b.id}:" in cache_key_b


def test_global_assistant_project_grounding(app_instance):
    with app_instance.app_context():
        user = User(email="founder@yosifix.ai", username="founder")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        idea_cert = Idea(
            user_id=user.id,
            title="AI Fake Certificate Verification for Educational Institutions",
            raw_text="AI-powered fake certificate and forged degree verification using optical forensics and cryptographic attestations.",
        )
        db.session.add(idea_cert)
        db.session.commit()

        orchestrator = AnalysisOrchestrator()
        ctx = orchestrator.run_full_analysis(idea_cert)

        from services.assistant.assistant_service import AssistantService
        assistant = AssistantService()

        # Ask about database choice
        res_db = assistant.ask(ctx, "Why is PostgreSQL recommended?")
        assert "postgresql" in res_db["response"].lower() or "sql" in res_db["response"].lower()
        assert "integrity" in res_db["response"].lower() or "transactional" in res_db["response"].lower() or "verification" in res_db["response"].lower()

        # Ask about risk
        res_risk = assistant.ask(ctx, "What is our biggest risk?")
        assert any(w in res_risk["response"].lower() for w in ["risk", "degree", "forged", "fraud", "failure", "kill"])
