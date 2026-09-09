from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        language = request.form.get("language", "en")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already registered.", "danger")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email, preferred_language=language)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        session["lang"] = language
        flash("Welcome to YosiFix! Your account is ready.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and user.check_password(password):
            login_user(user)
            session["lang"] = user.preferred_language or "en"
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid username/email or password.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("main.landing"))
