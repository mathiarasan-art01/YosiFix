import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["SECRET_KEY"] = "test-secret-key"

from app import app as flask_app  # noqa: E402


@pytest.fixture(scope="session")
def app():
    flask_app.config.update(TESTING=True)
    yield flask_app
    os.close(_db_fd)
    os.unlink(_db_path)


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
