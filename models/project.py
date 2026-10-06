"""Project (stored in the legacy ``ideas`` table), its versions and build prompts."""
from extensions import db
from models.base import utcnow


class Idea(db.Model):
    """A YosiFix project. The table name stays ``ideas`` for backward compatibility."""

    __tablename__ = "ideas"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(5), default="en")
    domain = db.Column(db.String(80))
    domain_confidence = db.Column(db.Float, default=0.0)
    innovation_score = db.Column(db.Float, default=0.0)
    current_version = db.Column(db.Integer, default=1)
    # New pipeline columns (added by migrate_db on existing databases)
    status = db.Column(db.String(30), default="draft")
    selected_mutation_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    versions = db.relationship(
        "IdeaVersion", backref="idea", lazy=True, cascade="all, delete-orphan",
        order_by="IdeaVersion.version_num",
    )
    prompts = db.relationship("PromptRecord", backref="idea", lazy=True, cascade="all, delete-orphan")
    stages = db.relationship("AnalysisStage", backref="idea", lazy=True, cascade="all, delete-orphan")
    evidence = db.relationship(
        "EvidenceSource", backref="idea", lazy=True, cascade="all, delete-orphan",
        order_by="EvidenceSource.code",
    )
    decisions = db.relationship(
        "UserOverride", backref="idea", lazy=True, cascade="all, delete-orphan",
        order_by="UserOverride.created_at",
    )
    judge_answers = db.relationship(
        "JudgeAnswer", backref="idea", lazy=True, cascade="all, delete-orphan",
        order_by="JudgeAnswer.created_at",
    )
    # Legacy one-to-one analysis row, kept so old databases still map cleanly.
    analysis = db.relationship(
        "AnalysisResult", backref="idea", lazy=True, cascade="all, delete-orphan", uselist=False
    )
    runs = db.relationship(
        "AnalysisRun", backref="idea", lazy=True, cascade="all, delete-orphan",
        order_by="AnalysisRun.started_at",
    )


# Friendlier alias used by the new code.
Project = Idea


class IdeaVersion(db.Model):
    __tablename__ = "idea_versions"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False, index=True)
    version_num = db.Column(db.Integer, nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    change_note = db.Column(db.String(255), default="")
    # New: who changed it, at which stage, and a metric snapshot for diffs
    actor = db.Column(db.String(20), default="user")
    stage = db.Column(db.String(40), default="idea")
    snapshot = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=utcnow)


ProjectVersion = IdeaVersion


class PromptRecord(db.Model):
    __tablename__ = "prompt_records"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False, index=True)
    target_tool = db.Column(db.String(30), nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
