from flask import Blueprint, render_template, session, request
from flask_login import login_required, current_user

from models import Idea
from modules.i18n import t

bp = Blueprint("main", __name__)


def current_lang():
    return session.get("lang", "en")


@bp.route("/")
def landing():
    if current_user.is_authenticated:
        from flask import redirect, url_for
        return redirect(url_for("main.dashboard"))
    return render_template("landing.html", lang=current_lang(), t=t)


@bp.route("/set-language/<lang_code>")
def set_language(lang_code):
    from flask import redirect, url_for
    if lang_code in ("en", "ta", "hi"):
        session["lang"] = lang_code
    return redirect(request.referrer or url_for("main.landing"))


@bp.route("/dashboard")
@login_required
def dashboard():
    ideas = Idea.query.filter_by(user_id=current_user.id).order_by(Idea.created_at.desc()).all()
    return render_template("dashboard.html", ideas=ideas, lang=current_lang(), t=t)
