from flask import (
    Blueprint, render_template, redirect, url_for, request, flash,
    session, send_file, current_app, abort
)
from flask_login import login_required, current_user

from extensions import db
from models import Idea, IdeaVersion, AnalysisResult, PromptRecord
from modules.i18n import t
from modules.classifier import classify_idea
from modules.similarity import analyze_similarity
from modules.gap_analysis import detect_gaps, compute_innovation_score
from modules.sdg_mapper import map_sdgs
from modules.tech_recommender import recommend_stack
from modules.architecture import generate_architecture_diagram
from modules.roadmap import generate_roadmap
from modules.prompt_studio import generate_master_prompt, TOOL_NOTES
from modules.blueprint_export import build_blueprint_docx
from modules.llm_client import LLMClient

bp = Blueprint("idea", __name__, url_prefix="/idea")


def current_lang():
    return session.get("lang", "en")


def get_llm_client():
    return LLMClient(
        groq_api_key=current_app.config.get("GROQ_API_KEY", ""),
        anthropic_api_key=current_app.config.get("ANTHROPIC_API_KEY", ""),
    )


def run_pipeline(idea_text, domain_hint=None):
    """Runs the full analysis pipeline and returns a dict of results.
    Never raises -- every stage has a deterministic rule-based path."""
    llm = get_llm_client()

    classification = classify_idea(idea_text, llm_client=llm)
    domain = domain_hint or classification["domain"]

    similarity = analyze_similarity(idea_text, domain)
    gaps = detect_gaps(idea_text, similarity["matches"])
    sdgs = map_sdgs(idea_text)
    stack = recommend_stack(idea_text, domain)
    architecture = generate_architecture_diagram(stack, domain)
    roadmap = generate_roadmap(gaps["gap_features"], stack)
    innovation_score = compute_innovation_score(
        similarity["overall_similarity"], len(gaps["gap_features"]), len(sdgs)
    )

    return {
        "classification": classification,
        "domain": domain,
        "similarity": similarity,
        "gaps": gaps,
        "sdgs": sdgs,
        "stack": stack,
        "architecture": architecture,
        "roadmap": roadmap,
        "innovation_score": innovation_score,
        "engine": classification.get("engine", "rule-based"),
    }


def persist_analysis(idea, results):
    analysis = idea.analysis
    if analysis is None:
        analysis = AnalysisResult(idea_id=idea.id)
        db.session.add(analysis)

    analysis.similar_solutions = results["similarity"]["matches"]
    analysis.overall_similarity = results["similarity"]["overall_similarity"]
    analysis.similarity_verdict = results["similarity"]["verdict"]
    analysis.covered_features = results["gaps"]["covered_features"]
    analysis.gap_features = results["gaps"]["gap_features"]
    analysis.opportunity_notes = results["gaps"]["opportunity_notes"]
    analysis.sdg_mappings = results["sdgs"]
    analysis.tech_stack = results["stack"]
    analysis.architecture_mermaid = results["architecture"]
    analysis.roadmap = results["roadmap"]
    analysis.engine_used = results["engine"]

    idea.domain = results["domain"]
    idea.domain_confidence = results["classification"]["confidence"]
    idea.innovation_score = results["innovation_score"]

    db.session.commit()
    return analysis


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

        results = run_pipeline(raw_text)
        persist_analysis(idea, results)

        flash("Analysis complete.", "success")
        return redirect(url_for("idea.result", idea_id=idea.id))

    return render_template("idea_new.html", lang=current_lang(), t=t)


@bp.route("/<int:idea_id>")
@login_required
def result(idea_id):
    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first_or_404()
    analysis = idea.analysis
    if analysis is None:
        results = run_pipeline(idea.raw_text)
        analysis = persist_analysis(idea, results)
    return render_template("idea_result.html", idea=idea, analysis=analysis, lang=current_lang(), t=t)


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

        results = run_pipeline(new_text)
        persist_analysis(idea, results)

        flash("Idea refined and re-analyzed.", "success")
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
