import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "yosifix-dev-secret-change-in-production")
    
    # On Vercel, root filesystem is read-only, so fallback SQLite must reside in /tmp
    if os.environ.get("VERCEL") and not os.environ.get("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/yosifix.db"
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'yosifix.db')}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optional LLM upgrade keys. If absent, every module falls back to its
    # rule-based engine automatically -- the app is fully functional with none of these set.
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

    LANGUAGES = ["en", "ta", "hi"]
    DEFAULT_LANGUAGE = "en"
