from flask import (
    Blueprint, render_template, redirect, url_for, request, flash,
    session, send_file, current_app, abort, jsonify
)
from flask_login import login_required, current_user

from extensions import db
from models import Idea, IdeaVersion, AnalysisResult, PromptRecord
from modules.i18n import t
from modules.prompt_studio import generate_master_prompt, TOOL_NOTES
from modules.blueprint_export import build_blueprint_docx
from services.analysis.orchestrator import AnalysisOrchestrator
from services.analysis.context import AnalysisContext
from services.groq.client import GroqClient

bp = Blueprint("idea", __name__, url_prefix="/idea")


def current_lang():
    return session.get("lang", "en")


def get_orchestrator():
    groq_key = current_app.config.get("GROQ_API_KEY", "")
    client = GroqClient(api_key=groq_key)
    return AnalysisOrchestrator(client=client)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        raw_text = request.form.get("idea_text", "").strip()
        title = request.form.get("title", "").strip()
        language = request.form.get("language", current_lang())

        if not raw_text or len(raw_text) < 15:
            flash("Please describe your idea in at least a sentence or two.", "danger")
            return redirect(url_for("idea.new"))

        if not title:
            title = raw_text[:60] + ("..." if len(raw_text) > 60 else "")

        idea = Idea(user_id=current_user.id, title=title, raw_text=raw_text, language=language)
        db.session.add(idea)
        db.session.commit()

        version = IdeaVersion(idea_id=idea.id, version_num=1, raw_text=raw_text, change_note="Initial submission")
        db.session.add(version)
        db.session.commit()

        # Run the full 15-stage unified analysis pipeline
        orchestrator = get_orchestrator()
        try:
            orchestrator.run_full_analysis(idea)
            flash("Evidence-backed analysis completed successfully.", "success")
        except Exception as exc:
            current_app.logger.exception(f"Pipeline error for idea {idea.id}: {exc}")
            flash(f"Analysis completed with baseline evaluation: {exc}", "warning")

        return redirect(url_for("idea.result", idea_id=idea.id))

    return render_template("idea_new.html", lang=current_lang(), t=t)


@bp.route("/<int:idea_id>")
@login_required
def result(idea_id):
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()
    analysis = idea.analysis
    
    # If analysis is missing or not yet upgraded to extended pipeline, run full analysis
    if analysis is None or not analysis.evidence or not analysis.novelty:
        orchestrator = get_orchestrator()
        orchestrator.run_full_analysis(idea)
        analysis = idea.analysis

    ctx = AnalysisContext.from_db(idea).to_dict()
    return render_template(
        "idea_result.html",
        idea=idea,
        analysis=analysis,
        ctx=ctx,
        lang=current_lang(),
        t=t,
    )


@bp.route("/<int:idea_id>/mutate", methods=["POST"])
@login_required
def mutate(idea_id):
    """User selects an architectural mutation."""
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()
    mutation_id = request.form.get("mutation_id", "").strip()

    if not mutation_id:
        flash("No mutation selected.", "warning")
        return redirect(url_for("idea.result", idea_id=idea.id))

    orchestrator = get_orchestrator()
    try:
        orchestrator.apply_mutation(idea, mutation_id)
        flash(f"Strategic pivot '{mutation_id}' applied. Architecture, roadmap, and defense updated!", "success")
    except Exception as exc:
        current_app.logger.exception(f"Failed to apply mutation {mutation_id}: {exc}")
        flash(f"Failed to apply mutation: {exc}", "danger")

    return redirect(url_for("idea.result", idea_id=idea.id))


@bp.route("/<int:idea_id>/judge-defense", methods=["POST"])
@login_required
def judge_defense(idea_id):
    """Evaluate user defense response via AJAX."""
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()
    question = request.form.get("question") or request.json.get("question", "")
    user_answer = request.form.get("answer") or request.json.get("answer", "")

    if not question or not user_answer:
        return jsonify({"error": "Question and answer are required"}), 400

    orchestrator = get_orchestrator()
    feedback = orchestrator.evaluate_judge_response(idea, question, user_answer)
    return jsonify({"status": "success", "feedback": feedback})


@bp.route("/<int:idea_id>/edit", methods=["GET", "POST"])
@login_required
def edit(idea_id):
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        new_text = request.form.get("idea_text", "").strip()
        note = request.form.get("change_note", "").strip() or "Refined idea"

        if not new_text or len(new_text) < 15:
            flash("Please provide updated idea text.", "danger")
            return redirect(url_for("idea.edit", idea_id=idea.id))

        idea.raw_text = new_text
        idea.current_version += 1
        db.session.commit()

        version = IdeaVersion(
            idea_id=idea.id, version_num=idea.current_version,
            raw_text=new_text, change_note=note,
        )
        db.session.add(version)
        db.session.commit()

        orchestrator = get_orchestrator()
        orchestrator.run_full_analysis(idea)

        flash("Idea refined and re-analyzed across all 15 stages.", "success")
        return redirect(url_for("idea.result", idea_id=idea.id))

    return render_template("idea_edit.html", idea=idea, lang=current_lang(), t=t)


@bp.route("/<int:idea_id>/history")
@login_required
def history(idea_id):
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()
    versions = IdeaVersion.query.filter_by(idea_id=idea.id).order_by(IdeaVersion.version_num).all()
    return render_template("idea_history.html", idea=idea, versions=versions, lang=current_lang(), t=t)


@bp.route("/<int:idea_id>/prompt-studio", methods=["GET", "POST"])
@login_required
def prompt_studio(idea_id):
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()
    analysis = idea.analysis
    if analysis is None:
        abort(400, "Analyze the idea before generating a build prompt.")

    generated_prompt = None
    target_tool = "claude"

    if request.method == "POST":
        target_tool = request.form.get("target_tool", "claude")
        generated_prompt = generate_master_prompt(idea, analysis, target_tool)

        record = PromptRecord(idea_id=idea.id, target_tool=target_tool, prompt_text=generated_prompt)
        db.session.add(record)
        db.session.commit()

    history_records = PromptRecord.query.filter_by(idea_id=idea.id).order_by(PromptRecord.created_at.desc()).limit(5).all()

    return render_template(
        "prompt_studio.html", idea=idea, analysis=analysis,
        generated_prompt=generated_prompt, target_tool=target_tool,
        tools=TOOL_NOTES.keys(), history_records=history_records,
        lang=current_lang(), t=t,
    )


@bp.route("/<int:idea_id>/export")
@login_required
def export(idea_id):
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()
    analysis = idea.analysis
    if analysis is None:
        abort(400, "Analyze the idea before exporting a blueprint.")

    latest_prompt = (
        PromptRecord.query.filter_by(idea_id=idea.id).order_by(PromptRecord.created_at.desc()).first()
    )
    prompt_text = latest_prompt.prompt_text if latest_prompt else None

    buf = build_blueprint_docx(idea, analysis, prompts=prompt_text)
    safe_name = "".join(c for c in idea.title if c.isalnum() or c in (" ", "_", "-")).strip()[:40] or "blueprint"
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"YosiFix_{safe_name}.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
