from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    preferred_language = db.Column(db.String(5), default="en")
    created_at = db.Column(db.DateTime, default=utcnow)

    ideas = db.relationship("Idea", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class Idea(db.Model):
    __tablename__ = "ideas"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(5), default="en")
    domain = db.Column(db.String(80))
    domain_confidence = db.Column(db.Float, default=0.0)
    innovation_score = db.Column(db.Float, default=0.0)
    current_version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    versions = db.relationship("IdeaVersion", backref="idea", lazy=True,
                                cascade="all, delete-orphan", order_by="IdeaVersion.version_num")
    analysis = db.relationship("AnalysisResult", backref="idea", lazy=True,
                                cascade="all, delete-orphan", uselist=False)
    prompts = db.relationship("PromptRecord", backref="idea", lazy=True,
                               cascade="all, delete-orphan")


class IdeaVersion(db.Model):
    __tablename__ = "idea_versions"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    version_num = db.Column(db.Integer, nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    change_note = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=utcnow)


class AnalysisResult(db.Model):
    __tablename__ = "analysis_results"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)

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

    engine_used = db.Column(db.String(20), default="rule-based")
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class PromptRecord(db.Model):
    __tablename__ = "prompt_records"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False)
    target_tool = db.Column(db.String(30), nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
