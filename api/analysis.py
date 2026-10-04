# api/analysis.py
"""REST API Blueprint for the YosiFix AI Analysis Pipeline.

Endpoints:
- POST /api/projects/<id>/analyze: Runs the full 15-stage analysis or initiates pipeline.
- GET  /api/projects/<id>/results: Fetches the complete structured analysis context.
- GET  /api/projects/<id>/status:  Fetches execution progress, completed stages, and engine used.
- POST /api/projects/<id>/mutate:  Applies a user-selected mutation and regenerates downstream outputs.
- POST /api/projects/<id>/judge/answer: Evaluates the user's defense against a judge attack question.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from extensions import db
from models import Idea, AnalysisResult
from services.analysis.orchestrator import AnalysisOrchestrator, STAGE_ORDER
from services.analysis.context import AnalysisContext
from services.groq.client import GroqClient

bp = Blueprint("analysis", __name__, url_prefix="/api")


def _get_orchestrator():
    groq_key = current_app.config.get("GROQ_API_KEY")
    client = GroqClient(api_key=groq_key)
    return AnalysisOrchestrator(client=client)


@bp.route("/projects/<int:project_id>/analyze", methods=["POST"])
@login_required
def analyze_project(project_id):
    """Run full 15-stage analysis pipeline for the specified project."""
    idea = Idea.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not idea:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    data = request.get_json(silent=True) or {}
    selected_mutation = data.get("mutation_id")

    # If raw_text is updated in payload, update idea
    if data.get("raw_text") and len(data["raw_text"].strip()) >= 15:
        idea.raw_text = data["raw_text"].strip()
        db.session.commit()

    orchestrator = _get_orchestrator()
    try:
        ctx = orchestrator.run_full_analysis(idea, selected_mutation_id=selected_mutation)
        return jsonify({
            "status": "success",
            "message": "Full analysis completed successfully",
            "project_id": idea.id,
            "data": ctx.to_dict(),
        })
    except Exception as exc:
        current_app.logger.exception(f"Analysis failed for project {project_id}: {exc}")
        return jsonify({"error": "Pipeline execution failed", "details": str(exc)}), 500


@bp.route("/projects/<int:project_id>/results", methods=["GET"])
@login_required
def get_analysis_results(project_id):
    """Retrieve full analysis context for a project."""
    idea = Idea.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not idea:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    ctx = AnalysisContext.from_db(idea)
    return jsonify({
        "status": "success",
        "project_id": idea.id,
        "data": ctx.to_dict(),
    })


@bp.route("/projects/<int:project_id>/status", methods=["GET"])
@login_required
def get_analysis_status(project_id):
    """Retrieve status and progress metrics for a project analysis."""
    idea = Idea.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not idea:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    ctx = AnalysisContext.from_db(idea)
    completed = ctx.completed_stages or []
    progress_pct = int(min(100, (len(completed) / max(1, len(STAGE_ORDER))) * 100))

    return jsonify({
        "project_id": idea.id,
        "current_stage": ctx.current_stage,
        "completed_stages": completed,
        "total_stages": len(STAGE_ORDER),
        "progress_percent": progress_pct,
        "engine_used": ctx.engine_used,
        "updated_at": ctx.updated_at,
    })


@bp.route("/projects/<int:project_id>/mutate", methods=["POST"])
@login_required
def apply_project_mutation(project_id):
    """User selects an architectural mutation. Downstream outputs are recomputed."""
    idea = Idea.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not idea:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    data = request.get_json(silent=True) or {}
    mutation_id = data.get("mutation_id")
    if not mutation_id:
        return jsonify({"error": "'mutation_id' is required"}), 400

    orchestrator = _get_orchestrator()
    try:
        ctx = orchestrator.apply_mutation(idea, mutation_id)
        return jsonify({
            "status": "success",
            "message": f"Mutation '{mutation_id}' applied successfully",
            "selected_mutation": ctx.selected_mutation_detail,
            "data": ctx.to_dict(),
        })
    except Exception as exc:
        current_app.logger.exception(f"Applying mutation failed: {exc}")
        return jsonify({"error": "Failed to apply mutation", "details": str(exc)}), 500


@bp.route("/projects/<int:project_id>/judge/answer", methods=["POST"])
@login_required
def evaluate_judge_answer(project_id):
    """Evaluate user defense against a judge attack question."""
    idea = Idea.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not idea:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    data = request.get_json(silent=True) or {}
    question = data.get("question")
    user_answer = data.get("answer")

    if not question or not user_answer:
        return jsonify({"error": "'question' and 'answer' fields are required"}), 400

    orchestrator = _get_orchestrator()
    try:
        feedback = orchestrator.evaluate_judge_response(idea, question, user_answer)
        return jsonify({
            "status": "success",
            "feedback": feedback,
        })
    except Exception as exc:
        current_app.logger.exception(f"Judge evaluation failed: {exc}")
        return jsonify({"error": "Failed to evaluate answer", "details": str(exc)}), 500


@bp.route("/projects/<int:project_id>/blueprint", methods=["GET"])
@login_required
def get_blueprint(project_id):
    """Retrieve full blueprint in structured JSON, markdown, or export."""
    idea = Idea.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not idea:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    ctx = AnalysisContext.from_db(idea).to_dict()
    blueprint = ctx.get("blueprint", {})
    from services.blueprint.blueprint_exporter import BlueprintExporter

    fmt = request.args.get("format", "json").lower()
    if fmt == "markdown":
        return BlueprintExporter.export_markdown(blueprint, context=ctx), 200, {"Content-Type": "text/markdown; charset=utf-8"}

    return jsonify({
        "status": "success",
        "project_id": idea.id,
        "blueprint": blueprint,
    })


@bp.route("/projects/<int:project_id>/chat", methods=["POST"])
@login_required
def assistant_chat(project_id):
    """Ask contextual questions to the project assistant."""
    idea = Idea.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not idea:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "'message' is required"}), 400

    ctx = AnalysisContext.from_db(idea)
    from services.assistant.assistant_service import AssistantService
    groq_key = current_app.config.get("GROQ_API_KEY", "")
    client = GroqClient(api_key=groq_key)
    assistant = AssistantService(groq_client=client)
    res = assistant.ask(ctx, message, chat_history=data.get("history", []))

    return jsonify({
        "status": "success",
        "reply": res["response"],
        "engine": res["engine"],
    })


@bp.route("/projects/<int:project_id>/evidence/refresh", methods=["POST"])
@login_required
def refresh_evidence(project_id):
    """Trigger real-time multi-source research for verified evidence."""
    idea = Idea.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not idea:
        return jsonify({"error": "Project not found or unauthorized"}), 404

    ctx = AnalysisContext.from_db(idea)
    try:
        from services.research.research_service import ResearchService
        research_svc = ResearchService()
        findings = research_svc.conduct_research(ctx.to_dict(), idea_id=idea.id)
        return jsonify({
            "status": "success",
            "count": len(findings),
            "evidence": findings,
        })
    except Exception as exc:
        current_app.logger.exception(f"Evidence refresh failed: {exc}")
        return jsonify({"error": "Evidence refresh failed", "details": str(exc)}), 500

