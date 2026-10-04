import pytest
from app import create_app
from extensions import db
from models import User, Idea, ChatMessage, AnalysisResult


@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "test_multiuser.db"
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db}",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_multiuser_registration_and_validation(client):
    # 1. Invalid email
    res = client.post("/auth/register", data={
        "username": "mu_val_user",
        "email": "invalid-email-address",
        "password": "password123",
        "password_confirm": "password123",
    }, follow_redirects=True)
    assert b"valid email" in res.data.lower()

    # 2. Password mismatch
    res = client.post("/auth/register", data={
        "username": "mu_val_user",
        "email": "mu_val_user@example.com",
        "password": "password123",
        "password_confirm": "different123",
    }, follow_redirects=True)
    assert b"match" in res.data.lower()

    # 3. Successful registration
    res = client.post("/auth/register", data={
        "username": "mu_val_user",
        "email": "mu_val_user@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "language": "en",
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome to YosiFix" in res.data

    # 4. Duplicate registration with same email
    res = client.post("/auth/register", data={
        "username": "mu_val_user2",
        "email": "MU_VAL_USER@EXAMPLE.COM",  # Case-insensitive
        "password": "password123",
        "password_confirm": "password123",
    }, follow_redirects=True)
    assert b"already exists" in res.data.lower()


def test_data_isolation_and_persistent_chat(client):
    # --- STEP 1: ALICE REGISTERS & CREATES DRONE PROJECT ---
    client.post("/auth/register", data={
        "username": "iso_alice",
        "email": "iso_alice@example.com",
        "password": "password123",
        "password_confirm": "password123",
    }, follow_redirects=True)

    # Alice creates a project
    create_res = client.post("/idea/new", data={
        "title": "Autonomous Drone for Power Line Inspection",
        "idea_text": "Autonomous edge-AI drone inspecting high-voltage power transmission lines detecting thermal hotspots and structural micro-cracks in real time without cloud dependence.",
    }, follow_redirects=True)
    assert create_res.status_code == 200

    # Retrieve Alice's idea id
    with client.application.app_context():
        alice = User.query.filter_by(email="iso_alice@example.com").first()
        alice_idea = Idea.query.filter_by(user_id=alice.id).first()
        assert alice_idea is not None
        alice_idea_id = alice_idea.id

    # Alice runs full analysis
    analyze_res = client.post(f"/api/projects/{alice_idea_id}/analyze", json={"force_refresh": True})
    assert analyze_res.status_code == 200
    analyze_data = analyze_res.get_json()
    assert analyze_data["status"] == "success"

    # Alice checks results: ensure analysis is for power lines/drones, NOT agriculture
    results_res = client.get(f"/api/projects/{alice_idea_id}/results")
    assert results_res.status_code == 200
    results_json = results_res.get_json()
    data = results_json["data"]
    assert "power" in data["original_idea"].lower() or "drone" in data["original_idea"].lower()
    assert "plantix" not in str(results_json).lower()

    # Alice sends a chat message
    chat_res = client.post(f"/idea/{alice_idea_id}/chat", json={
        "message": "What fail-safe is recommended when LiDAR encounters severe electromagnetic interference?",
    })
    assert chat_res.status_code == 200
    chat_json = chat_res.get_json()
    assert chat_json["status"] == "success"
    assert len(chat_json["reply"]) > 10

    # Alice fetches chat history
    history_res = client.get(f"/idea/{alice_idea_id}/chat")
    assert history_res.status_code == 200
    history_json = history_res.get_json()
    assert len(history_json["messages"]) == 2  # 1 user + 1 assistant
    assert history_json["messages"][0]["role"] == "user"
    assert "LiDAR" in history_json["messages"][0]["content"]

    # Alice logs out
    logout_res = client.get("/auth/logout", follow_redirects=True)
    assert logout_res.status_code == 200

    # --- STEP 2: BOB REGISTERS & CANNOT ACCESS ALICE'S PROJECT ---
    client.post("/auth/register", data={
        "username": "iso_bob",
        "email": "iso_bob@example.com",
        "password": "password456",
        "password_confirm": "password456",
    }, follow_redirects=True)

    # Bob's dashboard shows 0 projects
    dash_res = client.get("/dashboard")
    assert dash_res.status_code == 200
    assert b"Autonomous Drone" not in dash_res.data

    # Bob attempts to view Alice's project page -> 404
    bob_view = client.get(f"/idea/{alice_idea_id}")
    assert bob_view.status_code == 404

    # Bob attempts to access Alice's results via API -> 404
    bob_api = client.get(f"/api/projects/{alice_idea_id}/results")
    assert bob_api.status_code == 404

    # Bob attempts to access Alice's chat -> 404
    bob_chat = client.get(f"/idea/{alice_idea_id}/chat")
    assert bob_chat.status_code == 404

    # Bob creates his own project
    client.post("/idea/new", data={
        "title": "Decentralized Artisan Micro-Loans",
        "idea_text": "Micro-finance lending protocol connecting rural craftspeople to low-interest peer micro-loans using mobile wallet credit scoring.",
    }, follow_redirects=True)

    with client.application.app_context():
        bob = User.query.filter_by(email="iso_bob@example.com").first()
        bob_ideas = Idea.query.filter_by(user_id=bob.id).all()
        assert len(bob_ideas) == 1
        assert bob_ideas[0].title == "Decentralized Artisan Micro-Loans"

    # Bob logs out
    client.get("/auth/logout", follow_redirects=True)

    # --- STEP 3: ALICE LOGS BACK IN ---
    login_res = client.post("/auth/login", data={
        "identifier": "iso_alice@example.com",
        "password": "password123",
    }, follow_redirects=True)
    assert login_res.status_code == 200
    assert b"Welcome back, iso_alice" in login_res.data

    # Alice's dashboard has her drone project
    dash_res = client.get("/dashboard")
    assert b"Autonomous Drone for Power Line Inspection" in dash_res.data
    assert b"Decentralized Artisan Micro-Loans" not in dash_res.data

    # Alice's chat history is fully preserved
    history_res = client.get(f"/idea/{alice_idea_id}/chat")
    assert history_res.status_code == 200
    history_json = history_res.get_json()
    assert len(history_json["messages"]) == 2
    assert "LiDAR" in history_json["messages"][0]["content"]
