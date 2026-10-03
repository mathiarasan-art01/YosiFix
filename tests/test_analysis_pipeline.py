import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from app import create_app
from extensions import db
from models import User, Idea, AnalysisResult
from services.analysis.orchestrator import AnalysisOrchestrator, STAGE_ORDER
from services.analysis.context import AnalysisContext
from modules.blueprint_export import build_blueprint_docx


class TestAnalysisPipeline(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        self.user = User.query.filter_by(username="pipelinetester").first()
        if not self.user:
            self.user = User(username="pipelinetester", email="tester@yosifix.dev")
            self.user.set_password("pass1234")
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_full_15_stage_analysis(self):
        idea = Idea(
            user_id=self.user.id,
            title="AI Solar Panel Fault Detector",
            raw_text="A computer-vision drone system that scans utility-scale solar farms to detect micro-cracks and thermal anomalies in real time offline."
        )
        db.session.add(idea)
        db.session.commit()

        orchestrator = AnalysisOrchestrator()
        ctx = orchestrator.run_full_analysis(idea)

        # 1. Verify all 15 stages completed
        self.assertEqual(len(ctx.completed_stages), 15)
        self.assertEqual(set(STAGE_ORDER), set(ctx.completed_stages))

        # 2. Verify Idea Understanding
        self.assertTrue(bool(ctx.domain))
        self.assertTrue(len(ctx.target_users) > 0)
        self.assertTrue(bool(ctx.problem))

        # 3. Verify Evidence Board
        self.assertIn("claims", ctx.evidence)
        self.assertGreaterEqual(len(ctx.evidence["claims"]), 1)

        # 4. Verify Similarity & Novelty
        self.assertIsNotNone(ctx.similarity.get("overall_similarity_score"))
        self.assertIsNotNone(ctx.novelty.get("novelty_score"))
        self.assertGreater(len(ctx.novelty.get("unique_value_props", [])), 0)

        # 5. Verify Mutations
        self.assertGreaterEqual(len(ctx.mutations), 1)
        self.assertNotEqual(ctx.selected_mutation_detail, {})
        self.assertIsNotNone(ctx.selected_mutation_id)

        # 6. Verify Reality Check & Failures
        self.assertGreater(ctx.reality_check.get("buildability_score", 0), 0)
        self.assertGreater(len(ctx.failures.get("failure_modes", [])), 0)
        self.assertTrue(bool(ctx.failures.get("kill_factor")))

        # 7. Verify Technology & Architecture
        self.assertTrue(len(ctx.technology.get("recommended_stack", {})) > 0)
        arch_mermaid = ctx.architecture.get("mermaid_diagram", "")
        self.assertTrue("graph" in arch_mermaid or "flowchart" in arch_mermaid or len(arch_mermaid) > 10)

        # 8. Verify Judge Attack
        self.assertGreaterEqual(len(ctx.judge_attack.get("questions", [])), 1)

        # 9. Verify Blueprint & Export
        self.assertTrue(bool(ctx.blueprint.get("elevator_pitch")))
        docx_buf = build_blueprint_docx(idea, idea.analysis)
        self.assertIsNotNone(docx_buf.getvalue())
        self.assertGreater(len(docx_buf.getvalue()), 500)

    def test_mutation_pivot_workflow(self):
        idea = Idea(
            user_id=self.user.id,
            title="Smart Water Irrigation Mesh",
            raw_text="Autonomous soil moisture sensors that communicate over LoRa mesh networks to schedule precision drip irrigation without cellular data."
        )
        db.session.add(idea)
        db.session.commit()

        orchestrator = AnalysisOrchestrator()
        ctx = orchestrator.run_full_analysis(idea)

        # Pick second mutation
        available_mutations = ctx.mutations
        if len(available_mutations) > 1:
            new_mutation_id = available_mutations[1]["id"]
            updated_ctx = orchestrator.apply_mutation(idea, new_mutation_id)
            self.assertEqual(updated_ctx.selected_mutation_id, new_mutation_id)
            self.assertEqual(updated_ctx.selected_mutation_detail["id"], new_mutation_id)

    def test_judge_defense_evaluation(self):
        idea = Idea(
            user_id=self.user.id,
            title="Privacy First Medical Voice AI",
            raw_text="On-device clinical transcription that runs entirely on local hospital laptops with zero audio streaming to external clouds."
        )
        db.session.add(idea)
        db.session.commit()

        orchestrator = AnalysisOrchestrator()
        orchestrator.run_full_analysis(idea)

        evaluation = orchestrator.evaluate_judge_response(
            idea,
            question="How do you handle patient data privacy under HIPAA?",
            user_answer="All audio is processed on-device with zero network egress, fully audited local logs, and mathematical guarantees."
        )

        self.assertIn("score", evaluation)
        self.assertGreaterEqual(evaluation["score"], 60)
        self.assertIn("verdict", evaluation)
        self.assertIn("upgraded_rebuttal", evaluation)

    def test_api_endpoints(self):
        # 1. Log in through client
        res = self.client.post("/auth/login", data={"identifier": "pipelinetester", "password": "pass1234"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 2. Create test idea
        idea = Idea(
            user_id=self.user.id,
            title="Decentralized Energy Grid",
            raw_text="Peer-to-peer micro-grid energy trading for residential solar owners using local cryptographically signed ledgers."
        )
        db.session.add(idea)
        db.session.commit()

        # 3. Test POST /api/projects/<id>/analyze
        res = self.client.post(f"/api/projects/{idea.id}/analyze", json={})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)

        # 4. Test GET /api/projects/<id>/status
        res = self.client.get(f"/api/projects/{idea.id}/status")
        self.assertEqual(res.status_code, 200)
        status_data = res.get_json()
        self.assertEqual(status_data["total_stages"], 15)
        self.assertEqual(status_data["progress_percent"], 100)

        # 5. Test GET /api/projects/<id>/results
        res = self.client.get(f"/api/projects/{idea.id}/results")
        self.assertEqual(res.status_code, 200)
        results_data = res.get_json()
        self.assertIn("evidence", results_data["data"])
        self.assertIn("novelty", results_data["data"])

        # 6. Test POST /api/projects/<id>/judge/answer
        res = self.client.post(f"/api/projects/{idea.id}/judge/answer", json={
            "question": "What is the unit economics of residential grid balancing?",
            "answer": "Marginal transaction costs are zero because proof verification is processed locally."
        })
        self.assertEqual(res.status_code, 200)
        judge_data = res.get_json()
        self.assertEqual(judge_data["status"], "success")
        self.assertIn("feedback", judge_data)


if __name__ == "__main__":
    unittest.main()
