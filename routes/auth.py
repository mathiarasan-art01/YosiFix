import os
import re
import json
import base64
import urllib.parse
from flask import (
    Blueprint, render_template, redirect, url_for, request, flash,
    session, current_app, jsonify
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
import httpx

from extensions import db
from models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _generate_unique_username(base_name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "", base_name.replace(" ", "_"))[:20] or "user"
    candidate = cleaned
    counter = 1
    while User.query.filter(func.lower(User.username) == candidate.lower()).first():
        candidate = f"{cleaned}_{counter}"
        counter += 1
    return candidate


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET" and current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    google_client_id = current_app.config.get("GOOGLE_CLIENT_ID", "")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm")
        language = request.form.get("language", "en")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("auth.register"))

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.register"))

        if password_confirm is not None and password != password_confirm:
            flash("Passwords do not match. Please verify your password.", "danger")
            return redirect(url_for("auth.register"))

        # Case-insensitive duplicate check
        existing = User.query.filter(
            (func.lower(User.username) == username.lower()) |
            (func.lower(User.email) == email.lower())
        ).first()

        if existing:
            if existing.email.lower() == email.lower():
                flash("An account with this email already exists. Please log in.", "warning")
                return redirect(url_for("auth.login"))
            else:
                flash("This username is already taken. Please choose another.", "warning")
                return redirect(url_for("auth.register"))

        try:
            user = User(username=username, email=email, preferred_language=language)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Persistent login
            login_user(user, remember=True)
            session.permanent = True
            session["lang"] = language
            flash(f"Welcome to YosiFix, {user.username}! Your account is ready.", "success")
            return redirect(url_for("main.dashboard"))
        except Exception as exc:
            db.session.rollback()
            current_app.logger.exception(f"Registration error: {exc}")
            flash(f"Registration failed: {exc}", "danger")
            return redirect(url_for("auth.register"))

    return render_template(
        "auth/register.html",
        google_client_id=google_client_id,
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET" and current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    google_client_id = current_app.config.get("GOOGLE_CLIENT_ID", "")

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on" or True

        if not identifier or not password:
            flash("Please enter both username/email and password.", "danger")
            return redirect(url_for("auth.login"))

        # Case-insensitive lookup by username OR email
        user = User.query.filter(
            (func.lower(User.username) == identifier.lower()) |
            (func.lower(User.email) == identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            session.permanent = True
            session["lang"] = user.preferred_language or "en"
            flash(f"Logged in successfully. Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        # If previous user was active, log out
        logout_user()
        flash("Invalid username/email or password. Please check your credentials.", "danger")
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/login.html",
        google_client_id=google_client_id,
    )


@bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out safely.", "info")
    response = redirect(url_for("main.landing"))
    cookie_name = current_app.config.get("REMEMBER_COOKIE_NAME", "remember_token")
    response.delete_cookie(cookie_name)
    return response


# ---------------------------------------------------------------------------
# Google Sign-In & Register Flow
# ---------------------------------------------------------------------------

@bp.route("/google")
def google_auth():
    """Initiates standard Google OAuth 2.0 flow or offers demo login if keys absent."""
    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    if not client_id:
        # If client ID is not configured, redirect to demo google login with an alert
        return redirect(url_for("auth.google_demo"))

    # Compute callback URL
    redirect_uri = url_for("auth.google_callback", _external=True)
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode({
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "select_account",
        })
    )
    return redirect(google_auth_url)


@bp.route("/google/callback")
def google_callback():
    """Handles Google OAuth callback, exchanges code for user profile, logs in or registers."""
    code = request.args.get("code")
    if not code:
        error = request.args.get("error", "Access denied")
        flash(f"Google Sign-In canceled or failed: {error}", "warning")
        return redirect(url_for("auth.login"))

    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    client_secret = current_app.config.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = url_for("auth.google_callback", _external=True)

    try:
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        with httpx.Client(timeout=10) as client:
            token_resp = client.post(token_url, data=token_data)
            token_resp.raise_for_status()
            tokens = token_resp.json()
            access_token = tokens.get("access_token")

            # Fetch user profile
            userinfo_resp = client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            userinfo_resp.raise_for_status()
            profile = userinfo_resp.json()

        google_id = str(profile.get("sub", ""))
        email = profile.get("email", "").lower()
        name = profile.get("name") or email.split("@")[0]
        avatar = profile.get("picture")

        if not email:
            flash("Could not retrieve email address from your Google account.", "danger")
            return redirect(url_for("auth.login"))

        return _process_google_user(google_id, email, name, avatar)

    except Exception as exc:
        current_app.logger.exception(f"Google OAuth failed: {exc}")
        flash(f"Google authentication failed: {exc}", "danger")
        return redirect(url_for("auth.login"))


@bp.route("/google-one-tap", methods=["POST"])
def google_one_tap():
    """Handles Google Identity Services JWT credential from One Tap or Google button."""
    credential = request.form.get("credential") or (request.get_json(silent=True) or {}).get("credential")
    if not credential:
        return jsonify({"error": "No credential token provided"}), 400

    try:
        # Decode JWT payload without external heavy library (JWT is header.payload.signature)
        parts = credential.split(".")
        if len(parts) < 2:
            return jsonify({"error": "Malformed JWT token"}), 400

        # Base64 url-decode payload
        payload_b64 = parts[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64).decode("utf-8")
        payload = json.loads(payload_json)

        google_id = str(payload.get("sub", ""))
        email = payload.get("email", "").lower()
        name = payload.get("name") or email.split("@")[0]
        avatar = payload.get("picture")

        if not email:
            return jsonify({"error": "Email missing from token"}), 400

        user = _process_google_user_record(google_id, email, name, avatar)
        login_user(user, remember=True)
        session.permanent = True
        return jsonify({
            "status": "success",
            "message": f"Signed in as {user.username}",
            "redirect_url": url_for("main.dashboard"),
        })

    except Exception as exc:
        current_app.logger.exception(f"One-Tap decoding failed: {exc}")
        return jsonify({"error": f"One-Tap authentication failed: {exc}"}), 500


@bp.route("/google/demo")
def google_demo():
    """Instant 1-click test Google Sign-In for environments without registered OAuth credentials."""
    user = _process_google_user_record(
        google_id="demo_google_1029384756",
        email="google_demo_user@gmail.com",
        name="Google Test User",
        avatar="https://lh3.googleusercontent.com/a/default-user=s96-c",
    )
    login_user(user, remember=True)
    session.permanent = True
    flash(f"Signed in via Google account ({user.email})! Welcome, {user.username}.", "success")
    return redirect(url_for("main.dashboard"))


def _process_google_user(google_id: str, email: str, name: str, avatar: str = None):
    user = _process_google_user_record(google_id, email, name, avatar)
    login_user(user, remember=True)
    session.permanent = True
    flash(f"Successfully signed in with Google as {user.username} ({user.email})!", "success")
    return redirect(url_for("main.dashboard"))


def _process_google_user_record(google_id: str, email: str, name: str, avatar: str = None) -> User:
    # 1. Match by google_id
    user = User.query.filter_by(google_id=google_id).first() if google_id else None

    # 2. Or match by email
    if not user:
        user = User.query.filter(func.lower(User.email) == email.lower()).first()

    if user:
        # Link google_id if not already linked
        if google_id and not user.google_id:
            user.google_id = google_id
        if avatar and not user.avatar_url:
            user.avatar_url = avatar
        db.session.commit()
    else:
        # Auto-create new user with Google account
        username = _generate_unique_username(name)
        user = User(
            username=username,
            email=email,
            password_hash="GOOGLE_OAUTH_USER",
            google_id=google_id,
            avatar_url=avatar,
        )
        db.session.add(user)
        db.session.commit()

    return user
