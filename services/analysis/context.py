# services/analysis/context.py
"""AnalysisContext: Shared state container for the entire YosiFix analysis pipeline.

Every module reads from and writes to this context. This guarantees that:
- Every downstream module operates on the verified outputs of earlier stages.
- No disconnected, hallucinated, or ungrounded outputs are generated.
- User decisions (such as choosing an architectural mutation or answering judge questions)
  update the context and seamlessly propagate into downstream blueprints and architecture.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json


def _utcnow_iso():
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AnalysisContext:
    project_id: int
    original_idea: str
    normalized_idea: str = ""
    domain: str = "Technology"
    problem: str = ""
    target_users: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)

    # Stage outputs
    landscape: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    similarity: Dict[str, Any] = field(default_factory=dict)
    novelty: Dict[str, Any] = field(default_factory=dict)
    gaps: Dict[str, Any] = field(default_factory=dict)
    mutations: List[Dict[str, Any]] = field(default_factory=list)
    selected_mutation_id: Optional[str] = None
    selected_mutation_detail: Dict[str, Any] = field(default_factory=dict)
    reality_check: Dict[str, Any] = field(default_factory=dict)
    failures: Dict[str, Any] = field(default_factory=dict)
    impact: Dict[str, Any] = field(default_factory=dict)
    technology: Dict[str, Any] = field(default_factory=dict)
    architecture: Dict[str, Any] = field(default_factory=dict)
    roadmap: Dict[str, Any] = field(default_factory=dict)
    judge_attack: Dict[str, Any] = field(default_factory=dict)
    blueprint: Dict[str, Any] = field(default_factory=dict)

    # Pipeline metadata
    completed_stages: List[str] = field(default_factory=list)
    current_stage: str = "initialized"
    engine_used: str = "groq"
    updated_at: str = field(default_factory=_utcnow_iso)

    def select_mutation(self, mutation_id: str) -> bool:
        """Select a mutation and update selected_mutation_detail."""
        for m in self.mutations:
            if m.get("id") == mutation_id:
                m["selected"] = True
                self.selected_mutation_id = mutation_id
                self.selected_mutation_detail = m
            else:
                m["selected"] = False

        if not self.selected_mutation_detail and self.mutations:
            self.selected_mutation_id = self.mutations[0].get("id")
            self.selected_mutation_detail = self.mutations[0]
            self.mutations[0]["selected"] = True
        return bool(self.selected_mutation_detail)

    def mark_stage_completed(self, stage_name: str):
        if stage_name not in self.completed_stages:
            self.completed_stages.append(stage_name)
        self.current_stage = stage_name
        self.updated_at = _utcnow_iso()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisContext":
        valid_fields = cls.__dataclass_fields__.keys()
        clean_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**clean_data)

    @classmethod
    def from_db(cls, idea) -> "AnalysisContext":
        """Reconstruct context from an Idea model instance and its AnalysisResult."""
        analysis = getattr(idea, "analysis", None)
        ctx = cls(
            project_id=idea.id,
            original_idea=idea.raw_text,
            normalized_idea=idea.title,
            domain=idea.domain or "Technology",
        )

        if analysis:
            ctx.engine_used = getattr(analysis, "engine_used", "groq") or "groq"
            ctx.similarity = {
                "matches": getattr(analysis, "similar_solutions", []) or [],
                "overall_similarity_score": getattr(analysis, "overall_similarity", 0.0) or 0.0,
                "similarity_verdict": getattr(analysis, "similarity_verdict", "") or "",
            }
            ctx.gaps = {
                "covered_features": getattr(analysis, "covered_features", []) or [],
                "gap_features": getattr(analysis, "gap_features", []) or [],
                "opportunity_notes": getattr(analysis, "opportunity_notes", []) or [],
            }
            ctx.impact = {
                "sdg_mappings": getattr(analysis, "sdg_mappings", []) or [],
            }
            ctx.technology = getattr(analysis, "tech_stack", {}) or {}
            ctx.architecture = {
                "mermaid_diagram": getattr(analysis, "architecture_mermaid", "") or "",
            }
            ctx.roadmap = getattr(analysis, "roadmap", {}) or {}

            # Load extended pipeline fields if present
            for ext_field in [
                "landscape", "evidence", "novelty", "mutations",
                "selected_mutation_id", "selected_mutation_detail",
                "reality_check", "failures", "judge_attack", "blueprint",
                "completed_stages", "current_stage"
            ]:
                if hasattr(analysis, ext_field):
                    val = getattr(analysis, ext_field)
                    if val is not None:
                        setattr(ctx, ext_field, val)

            # Ensure normalized_idea and problem are loaded
            if hasattr(analysis, "normalized_idea") and analysis.normalized_idea:
                ctx.normalized_idea = analysis.normalized_idea
            if hasattr(analysis, "problem") and analysis.problem:
                ctx.problem = analysis.problem
            if hasattr(analysis, "target_users") and analysis.target_users:
                ctx.target_users = analysis.target_users
            if hasattr(analysis, "keywords") and analysis.keywords:
                ctx.keywords = analysis.keywords

        return ctx

    def sync_to_db(self, idea, db_session):
        """Persist the current context into the Idea and AnalysisResult models."""
        from models import AnalysisResult

        analysis = getattr(idea, "analysis", None)
        if analysis is None:
            analysis = AnalysisResult(idea_id=idea.id)
            db_session.add(analysis)

        # Base fields mapped to original columns
        analysis.similar_solutions = self.similarity.get("feature_overlap", self.similarity.get("matches", []))
        analysis.overall_similarity = float(self.similarity.get("overall_similarity_score", 0.0))
        analysis.similarity_verdict = str(self.similarity.get("similarity_verdict", ""))

        analysis.covered_features = self.gaps.get("covered_features", self.requirements)
        analysis.gap_features = self.gaps.get("unmet_needs", self.gaps.get("gap_features", []))
        analysis.opportunity_notes = self.gaps.get("recommended_angles", self.gaps.get("opportunity_notes", []))

        analysis.sdg_mappings = self.impact.get("sdg_alignments", self.impact.get("sdg_mappings", []))
        analysis.tech_stack = self.technology.get("recommended_stack", self.technology)
        analysis.architecture_mermaid = self.architecture.get("mermaid_diagram", "")
        analysis.roadmap = self.roadmap.get("phases", self.roadmap)
        analysis.engine_used = self.engine_used

        # Extended fields
        for ext_field in [
            "landscape", "evidence", "novelty", "mutations",
            "selected_mutation_id", "selected_mutation_detail",
            "reality_check", "failures", "judge_attack", "blueprint",
            "completed_stages", "current_stage",
            "normalized_idea", "problem", "target_users", "keywords"
        ]:
            if hasattr(analysis, ext_field):
                setattr(analysis, ext_field, getattr(self, ext_field))

        # Update Idea model
        if self.domain:
            idea.domain = self.domain
        if self.novelty and "novelty_score" in self.novelty:
            idea.innovation_score = float(self.novelty["novelty_score"])

        db_session.commit()
        return analysis
