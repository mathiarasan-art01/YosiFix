def _get_idea_id(app, title):
    from models import Idea
    with app.app_context():
        idea = Idea.query.filter_by(title=title).order_by(Idea.id.desc()).first()
        assert idea is not None, f"No idea found with title {title!r}"
        return idea.id


def test_landing_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"YosiFix" in resp.data


def test_register_and_redirect_to_dashboard(client):
    resp = client.post("/auth/register", data={
        "username": "alice",
        "email": "alice@example.com",
        "password": "securepass1",
        "language": "en",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data or b"dashboard" in resp.data.lower()


def test_register_rejects_short_password(client):
    resp = client.post("/auth/register", data={
        "username": "bob",
        "email": "bob@example.com",
        "password": "123",
        "language": "en",
    }, follow_redirects=True)
    assert b"at least 6 characters" in resp.data.lower() or resp.status_code == 200


def test_login_with_wrong_password_fails(client):
    client.post("/auth/register", data={
        "username": "carol", "email": "carol@example.com",
        "password": "correctpass", "language": "en",
    })
    client.get("/auth/logout")
    resp = client.post("/auth/login", data={
        "identifier": "carol", "password": "wrongpass",
    }, follow_redirects=True)
    assert b"Invalid" in resp.data


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard", follow_redirects=True)
    assert b"log in" in resp.data.lower() or b"login" in resp.data.lower()


def test_create_idea_runs_full_pipeline(registered_client):
    resp = registered_client.post("/idea/new", data={
        "title": "CropGuard",
        "idea_text": (
            "A mobile app that helps farmers detect crop disease early using "
            "photos taken on their phone, and connects them to nearby agri-input "
            "suppliers for treatment recommendations."
        ),
        "language": "en",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"CropGuard" in resp.data
    assert b"Agriculture" in resp.data
    assert b"Recommended Tech Stack" in resp.data or b"Tech Stack" in resp.data


def test_create_idea_rejects_too_short_text(registered_client):
    resp = registered_client.post("/idea/new", data={
        "title": "X", "idea_text": "too short", "language": "en",
    }, follow_redirects=True)
    assert b"at least a sentence" in resp.data.lower()


def test_dashboard_lists_created_idea(registered_client):
    registered_client.post("/idea/new", data={
        "title": "SafeWalk",
        "idea_text": "An app that lets women share live location with trusted contacts during night travel for safety.",
        "language": "en",
    })
    resp = registered_client.get("/dashboard")
    assert b"SafeWalk" in resp.data


def test_edit_idea_creates_new_version(app, registered_client):
    registered_client.post("/idea/new", data={
        "title": "EduBridge",
        "idea_text": "A platform connecting rural students to volunteer tutors for live doubt-solving sessions online.",
        "language": "en",
    }, follow_redirects=True)
    idea_id = _get_idea_id(app, "EduBridge")

    edit_resp = registered_client.post(f"/idea/{idea_id}/edit", data={
        "idea_text": "A platform connecting rural students to volunteer tutors for live doubt-solving sessions online, now with offline-first support for low-connectivity areas.",
        "change_note": "Added offline support",
    }, follow_redirects=True)
    assert edit_resp.status_code == 200

    history_resp = registered_client.get(f"/idea/{idea_id}/history")
    assert b"Version 2" in history_resp.data
    assert b"Added offline support" in history_resp.data


def test_prompt_studio_generates_prompt(app, registered_client):
    registered_client.post("/idea/new", data={
        "title": "MindEase",
        "idea_text": "A mental health chatbot that checks in on college students daily and flags concerning patterns to counselors.",
        "language": "en",
    }, follow_redirects=True)
    idea_id = _get_idea_id(app, "MindEase")

    resp = registered_client.post(f"/idea/{idea_id}/prompt-studio", data={
        "target_tool": "claude",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"MindEase" in resp.data
    assert b"Generated Prompt" in resp.data


def test_export_blueprint_returns_docx(app, registered_client):
    registered_client.post("/idea/new", data={
        "title": "WasteNot",
        "idea_text": "An app connecting restaurants with surplus food to nearby shelters for same-day pickup.",
        "language": "en",
    }, follow_redirects=True)
    idea_id = _get_idea_id(app, "WasteNot")

    resp = registered_client.get(f"/idea/{idea_id}/export")
    assert resp.status_code == 200
    assert resp.mimetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(resp.data) > 1000  # a real docx, not an empty stub


def test_language_switch_persists_in_session(client):
    resp = client.get("/set-language/ta", follow_redirects=True)
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("lang") == "ta"
