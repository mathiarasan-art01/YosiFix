from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.base import utcnow

GOOGLE_ONLY_SENTINEL = "GOOGLE_OAUTH_USER"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    preferred_language = db.Column(db.String(5), default="en")
    created_at = db.Column(db.DateTime, default=utcnow)

    ideas = db.relationship("Idea", backref="owner", lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship(
        "Notification", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def has_password(self):
        return bool(self.password_hash) and self.password_hash != GOOGLE_ONLY_SENTINEL

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password) if raw_password else None

    def check_password(self, raw_password):
        if not self.has_password or not raw_password:
            return False
        return check_password_hash(self.password_hash, raw_password)

    @property
    def initials(self):
        return (self.username or "?")[:2].upper()
