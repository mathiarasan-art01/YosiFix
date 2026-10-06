# services/analysis/orchestrator.py
"""AnalysisOrchestrator: The central brain of the YosiFix analysis pipeline.

Coordinates the 15-stage analysis pipeline, ensuring that:
1. Every stage executes in dependency order with verified previous inputs.
2. Context is maintained and persisted across steps.
3. User decisions (like selecting a mutation) invalidate and update downstream stages.
4. If Groq is configured, LLM reasoning is used; otherwise, the resilient deterministic
   rule engine seamlessly powers the analysis without failing.
"""

import logging
from typing import Optional, Dict, Any, List

from extensions import db
from models import Idea, AnalysisResult
from services.groq.client import GroqClient
from services.analysis.context import AnalysisContext

logger = logging.getLogger("yosifix.orchestrator")


STAGE_ORDER = [
    "idea_understanding",
    "solution_landscape",
    "evidence_board",
    "similarity_analysis",
    "novelty_score",
    "research_gap",
    "mutation_engine",
    "reality_check",
    "failure_simulation",
    "impact_and_sdg",
    "technology_decision",
    "architecture",
    "roadmap",
    "judge_attack",
    "master_blueprint",
]


class AnalysisOrchestrator:
    def __init__(self, client: Optional[GroqClient] = None):
        if client is not None:
            self.client = client
        else:
            try:
                from flask import current_app, has_app_context
                if has_app_context() and current_app and hasattr(current_app, "config"):
                    self.client = GroqClient.from_app(current_app)
                else:
                    self.client = GroqClient()
            except Exception:
                self.client = GroqClient()

    def run_full_analysis(
        self,
        idea: Idea,
        selected_mutation_id: Optional[str] = None,
        db_session=None,
    ) -> AnalysisContext:
        """Run the end-to-end 15-stage pipeline for an idea and persist results."""
        session = db_session or db.session
        ctx = AnalysisContext.from_db(idea)
        raw_text = idea.raw_text

        ctx.engine_used = self.client.active_engine() if hasattr(self.client, "active_engine") else ("groq" if self.client.is_configured() else "rule-based")

        # Stage 1: Idea Understanding
        idea_res = self.client.analyze_idea(raw_text)
        ctx.normalized_idea = idea_res.normalized_idea
        ctx.target_users = idea_res.target_users
        ctx.domain = idea_res.domain
        ctx.problem = idea_res.problem
        ctx.keywords = idea_res.keywords
        ctx.constraints = idea_res.constraints
        ctx.requirements = idea_res.requirements
        ctx.mark_stage_completed("idea_understanding")

        # Stage 2: Solution Landscape
        landscape_res = self.client.analyze_landscape(ctx.to_dict())
        ctx.landscape = landscape_res.to_dict()
        ctx.mark_stage_completed("solution_landscape")

        # Stage 3: Evidence Board
        evidence_res = self.client.verify_evidence(ctx.to_dict())
        ctx.evidence = evidence_res.to_dict()
        try:
            from services.research.research_service import ResearchService
            research_svc = ResearchService()
            external_evidence = research_svc.conduct_research(ctx.to_dict(), idea_id=idea.id)
            if external_evidence:
                ctx.evidence["evidence_sources"] = external_evidence
        except Exception as e:
            logger.warning(f"External evidence gathering skipped: {e}")
        ctx.mark_stage_completed("evidence_board")

        # Stage 4: Similarity Analysis
        sim_res = self.client.analyze_similarity(ctx.to_dict())
        ctx.similarity = sim_res.to_dict()
        ctx.mark_stage_completed("similarity_analysis")

        # Stage 5: Novelty Score
        novelty_res = self.client.score_novelty(ctx.to_dict())
        ctx.novelty = novelty_res.to_dict()
        ctx.mark_stage_completed("novelty_score")

        # Stage 6: Research & Market Gaps
        gap_res = self.client.find_gaps(ctx.to_dict())
        ctx.gaps = gap_res.to_dict()
        ctx.mark_stage_completed("research_gap")

        # Stage 7: Mutation Engine
        mutation_res = self.client.generate_mutations(ctx.to_dict())
        ctx.mutations = [m.to_dict() for m in mutation_res.mutations]
        target_mutation = selected_mutation_id or (ctx.mutations[0]["id"] if ctx.mutations else None)
        if target_mutation:
            ctx.select_mutation(target_mutation)
        ctx.mark_stage_completed("mutation_engine")

        # Stage 8: Reality Check
        reality_res = self.client.reality_check(ctx.to_dict())
        ctx.reality_check = reality_res.to_dict()
        ctx.mark_stage_completed("reality_check")

        # Stage 9: Failure Simulation
        fail_res = self.client.simulate_failures(ctx.to_dict())
        ctx.failures = fail_res.to_dict()
        ctx.mark_stage_completed("failure_simulation")

        # Stage 10: Impact & SDG
        impact_res = self.client.map_impact(ctx.to_dict())
        ctx.impact = impact_res.to_dict()
        ctx.mark_stage_completed("impact_and_sdg")

        # Stage 11: Technology Decision
        tech_res = self.client.recommend_technology(ctx.to_dict())
        ctx.technology = tech_res.to_dict()
        ctx.mark_stage_completed("technology_decision")

        # Stage 12: Architecture & Mermaid
        arch_res = self.client.generate_architecture(ctx.to_dict())
        ctx.architecture = arch_res.to_dict()
        ctx.mark_stage_completed("architecture")

        # Stage 13: Roadmap
        roadmap_res = self.client.generate_roadmap(ctx.to_dict())
        ctx.roadmap = roadmap_res.to_dict()
        ctx.mark_stage_completed("roadmap")

        # Stage 14: Judge Attack
        judge_res = self.client.generate_judge_questions(ctx.to_dict())
        ctx.judge_attack = judge_res.to_dict()
        ctx.mark_stage_completed("judge_attack")

        # Stage 15: Master Blueprint
        blueprint_res = self.client.generate_blueprint(ctx.to_dict())
        ctx.blueprint = blueprint_res.to_dict()
        ctx.mark_stage_completed("master_blueprint")

        # Persist full state to DB
        ctx.sync_to_db(idea, session)
        return ctx

    def apply_mutation(
        self,
        idea: Idea,
        mutation_id: str,
        db_session=None,
    ) -> AnalysisContext:
        """User chose a mutation. Update the mutation and re-run downstream stages."""
        session = db_session or db.session
        ctx = AnalysisContext.from_db(idea)

        if not ctx.mutations:
            # If no mutations recorded yet, run full analysis
            return self.run_full_analysis(idea, selected_mutation_id=mutation_id, db_session=session)

        # Select the chosen mutation and invalidate downstream stages
        ctx.select_mutation(mutation_id)
        from services.analysis.invalidation import InvalidationManager
        InvalidationManager.invalidate_for_mutation_selection(ctx)

        # Downstream stages dependent on the mutation
        reality_res = self.client.reality_check(ctx.to_dict())
        ctx.reality_check = reality_res.to_dict()
        ctx.mark_stage_completed("reality_check")

        fail_res = self.client.simulate_failures(ctx.to_dict())
        ctx.failures = fail_res.to_dict()
        ctx.mark_stage_completed("failure_simulation")

        tech_res = self.client.recommend_technology(ctx.to_dict())
        ctx.technology = tech_res.to_dict()
        ctx.mark_stage_completed("technology_decision")

        arch_res = self.client.generate_architecture(ctx.to_dict())
        ctx.architecture = arch_res.to_dict()
        ctx.mark_stage_completed("architecture")

        roadmap_res = self.client.generate_roadmap(ctx.to_dict())
        ctx.roadmap = roadmap_res.to_dict()
        ctx.mark_stage_completed("roadmap")

        judge_res = self.client.generate_judge_questions(ctx.to_dict())
        ctx.judge_attack = judge_res.to_dict()
        ctx.mark_stage_completed("judge_attack")

        blueprint_res = self.client.generate_blueprint(ctx.to_dict())
        ctx.blueprint = blueprint_res.to_dict()
        ctx.mark_stage_completed("master_blueprint")

        ctx.sync_to_db(idea, session)
        return ctx

    def evaluate_judge_response(
        self,
        idea: Idea,
        question: str,
        user_answer: str,
    ) -> Dict[str, Any]:
        """Evaluate a user's answer to a judge question."""
        ctx = AnalysisContext.from_db(idea)
        return self.client.evaluate_judge_answer(question, user_answer, ctx.to_dict())
