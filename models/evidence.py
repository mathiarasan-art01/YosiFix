"""Evidence retrieved from real external sources. Every AI claim may only cite these codes."""
from extensions import db
from models.base import utcnow


class EvidenceSource(db.Model):
    __tablename__ = "evidence_sources"
    __table_args__ = (db.UniqueConstraint("idea_id", "code", name="uq_evidence_code"),)

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.id"), nullable=False, index=True)
    code = db.Column(db.String(12), nullable=False)          # EV-001
    type = db.Column(db.String(20), nullable=False)          # github | paper | dataset | product | discussion | documentation
    title = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(600), default="")
    source_name = db.Column(db.String(60), default="")
    description = db.Column(db.Text, default="")
    published_at = db.Column(db.String(30), default="")
    metrics = db.Column(db.JSON, default=dict)               # stars, citations, downloads, points...
    relevance = db.Column(db.Float, default=0.0)             # 0..1 lexical relevance to the idea
    query = db.Column(db.String(200), default="")
    # verified = fetched live from the source API; curated = from the offline catalog
    verification_status = db.Column(db.String(20), default="verified")
    retrieved_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "code": self.code,
            "type": self.type,
            "title": self.title,
            "url": self.url,
            "source_name": self.source_name,
            "description": self.description,
            "published_at": self.published_at,
            "metrics": self.metrics or {},
            "relevance": round(self.relevance or 0.0, 3),
            "query": self.query,
            "verification_status": self.verification_status,
        }
