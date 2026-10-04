"""Analysis state: one row per pipeline stage per project, plus a result cache and unified AnalysisResult."""
from extensions import db
from models.base import utcnow


class AnalysisStage(db.Model):
    __tablename__ = "analysis_stages"
    __table_args__ = (db.UniqueConstraint("idea_id", "stage_key", name="uq_stage_per_project"),)

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False, index=True)
    stage_key = db.Column(db.String(40), nullable=False)
    # pending | running | done | stale | error | awaiting_decision
    status = db.Column(db.String(20), default="pending", nullable=False)
    output = db.Column(db.JSON, default=dict)
    engine = db.Column(db.String(80), default="")
    confidence = db.Column(db.Integer, default=0)
    input_hash = db.Column(db.String(64), default="")
    output_hash = db.Column(db.String(64), default="")
    error = db.Column(db.Text, default="")
    duration_ms = db.Column(db.Integer, default=0)
    run_count = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class AnalysisCache(db.Model):
    """Content-addressed cache: identical stage inputs never trigger a second Groq call."""

    __tablename__ = "analysis_cache"

    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    stage_key = db.Column(db.String(40), nullable=False)
    output = db.Column(db.JSON, default=dict)
    engine = db.Column(db.String(80), default="")
    hits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)


class AnalysisResult(db.Model):
    __tablename__ = "analysis_results"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False, index=True)

    similar_solutions = db.Column(db.JSON, default=list)
    overall_similarity = db.Column(db.Float, default=0.0)
    similarity_verdict = db.Column(db.String(255), default="")

    covered_features = db.Column(db.JSON, default=list)
    gap_features = db.Column(db.JSON, default=list)
    opportunity_notes = db.Column(db.JSON, default=list)

    sdg_mappings = db.Column(db.JSON, default=list)

    tech_stack = db.Column(db.JSON, default=dict)
    architecture_mermaid = db.Column(db.Text, default="")

    roadmap = db.Column(db.JSON, default=dict)

    engine_used = db.Column(db.String(40), default="rule-based")
    
    # Extended 15-stage pipeline columns
    normalized_idea = db.Column(db.Text, default="")
    problem = db.Column(db.Text, default="")
    target_users = db.Column(db.JSON, default=list)
    keywords = db.Column(db.JSON, default=list)
    landscape = db.Column(db.JSON, default=dict)
    evidence = db.Column(db.JSON, default=dict)
    novelty = db.Column(db.JSON, default=dict)
    mutations = db.Column(db.JSON, default=list)
    selected_mutation_id = db.Column(db.String(100), default="")
    selected_mutation_detail = db.Column(db.JSON, default=dict)
    reality_check = db.Column(db.JSON, default=dict)
    failures = db.Column(db.JSON, default=dict)
    judge_attack = db.Column(db.JSON, default=dict)
    blueprint = db.Column(db.JSON, default=dict)
    completed_stages = db.Column(db.JSON, default=list)
    current_stage = db.Column(db.String(50), default="initialized")

    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
