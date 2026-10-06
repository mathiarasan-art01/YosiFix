import os
from datetime import timedelta

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load .env for local development. On Vercel, variables come from the dashboard
# and an existing environment variable always wins over the file.
load_dotenv(os.path.join(BASE_DIR, ".env"), override=False)

IS_VERCEL = bool(os.environ.get("VERCEL"))
IS_RENDER = bool(os.environ.get("RENDER"))
_DEFAULT_SECRET = "yosifix-dev-secret-change-in-production"


def _database_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        # Heroku/Neon/Render style URLs use postgres:// which SQLAlchemy 2 rejects.
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        # On serverless (Vercel/Lambda), if psycopg2 isn't available or fails, use pure-python pg8000
        if (IS_VERCEL or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")) and url.startswith("postgresql://"):
            try:
                import psycopg2  # noqa
            except ImportError:
                url = "postgresql+pg8000://" + url[len("postgresql://"):]
        return url

    # On Vercel / serverless runtimes, filesystem is read-only except /tmp
    if IS_VERCEL or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "sqlite:////tmp/yosifix.db"

    # Local / Render default: test if instance directory can be created and written
    inst_dir = os.path.join(BASE_DIR, "instance")
    try:
        os.makedirs(inst_dir, exist_ok=True)
        test_file = os.path.join(inst_dir, ".perm_check")
        with open(test_file, "w") as f:
            f.write("1")
        if os.path.exists(test_file):
            os.remove(test_file)
        return f"sqlite:///{os.path.join(inst_dir, 'yosifix.db')}"
    except Exception:
        # Fallback to /tmp if filesystem is non-writable
        return "sqlite:////tmp/yosifix.db"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", _DEFAULT_SECRET)
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    # Sessions: 30-day persistent login
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_VERCEL or IS_RENDER
    REMEMBER_COOKIE_SECURE = IS_VERCEL or IS_RENDER

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # OpenAI Provider
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()
    OPENAI_TIMEOUT = int(os.environ.get("OPENAI_TIMEOUT", "60"))

    # Research sources (optional token raises GitHub's rate limit from 10 to 30 searches/min)
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
    RESEARCH_TIMEOUT = float(os.environ.get("RESEARCH_TIMEOUT", "8"))
    RESEARCH_CONTACT_EMAIL = os.environ.get("RESEARCH_CONTACT_EMAIL", "").strip()

    # Google Sign-In (optional)
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()

    # The shared demo account is only available when explicitly enabled.
    ENABLE_DEMO_LOGIN = os.environ.get("ENABLE_DEMO_LOGIN", "1" if not IS_VERCEL else "0") == "1"

    LANGUAGES = ["en", "ta", "hi"]
    DEFAULT_LANGUAGE = "en"

    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB request bodies
    RATELIMIT_ENABLED = True


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    GROQ_API_KEY = ""
    WTF_CSRF_ENABLED = False
    CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    RESEARCH_OFFLINE = True
    ENABLE_DEMO_LOGIN = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
