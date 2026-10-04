import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["GROQ_API_KEY"] = ""

from app import app as flask_app  # noqa: E402


@pytest.fixture(scope="session")
def app():
    flask_app.config.update(TESTING=True, GROQ_API_KEY="", CSRF_ENABLED=False)
    yield flask_app
    try:
        os.close(_db_fd)
    except OSError:
        pass
    try:
        os.unlink(_db_path)
    except OSError:
        pass


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def registered_client(client):
    import uuid
    suffix = uuid.uuid4().hex[:8]
    client.post("/auth/register", data={
        "username": f"testuser_{suffix}",
        "email": f"test_{suffix}@example.com",
        "password": "password123",
        "language": "en",
    }, follow_redirects=True)
    return client
