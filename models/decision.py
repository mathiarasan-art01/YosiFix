"""User decisions and overrides. AI recommendations never silently overwrite these."""
from extensions import db
from models.base import utcnow


class UserOverride(db.Model):
    __tablename__ = "user_overrides"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False, index=True)
    # mutation_selection | technology | requirement | roadmap | architecture
    kind = db.Column(db.String(30), nullable=False)
    target = db.Column(db.String(120), default="")          # e.g. technology layer "Backend"
    ai_recommendation = db.Column(db.Text, default="")
    user_decision = db.Column(db.Text, default="")
    reason = db.Column(db.Text, default="")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "target": self.target,
            "ai_recommendation": self.ai_recommendation,
            "user_decision": self.user_decision,
            "reason": self.reason,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class JudgeAnswer(db.Model):
    __tablename__ = "judge_answers"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False, index=True)
    question_id = db.Column(db.String(12), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, default=0)
    strength = db.Column(db.String(20), default="Weak")
    feedback = db.Column(db.JSON, default=dict)
    engine = db.Column(db.String(80), default="")
    created_at = db.Column(db.DateTime, default=utcnow)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id", ondelete="CASCADE"), nullable=True)
    kind = db.Column(db.String(30), default="info")
    message = db.Column(db.String(300), nullable=False)
    link = db.Column(db.String(300), default="")
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)
