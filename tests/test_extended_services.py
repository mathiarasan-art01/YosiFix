"""Tests for extended services: BlueprintExporter, AssistantService, InvalidationManager, Cache, and new routes."""
import json
import io
import pytest
from services.analysis.context import AnalysisContext
from services.analysis.dependency_graph import DependencyGraph, PIPELINE_STAGES
from services.analysis.invalidation import InvalidationManager
from services.analysis.cache import AnalysisCacheService
from services.blueprint.blueprint_exporter import BlueprintExporter
from services.assistant.assistant_service import AssistantService
from services.assistant.context_builder import AssistantContextBuilder
from models import Idea, User


def test_dependency_graph():
    stages = DependencyGraph.get_stage_order()
    assert len(stages) == 15
    assert stages[0] == "idea_understanding"
    assert stages[-1] == "master_blueprint"

    downstream = DependencyGraph.get_downstream_stages("mutation_engine")
    assert "reality_check" in downstream
    assert "architecture" in downstream
    assert "master_blueprint" in downstream


def test_invalidation_manager():
    ctx = AnalysisContext(
        project_id=1,
        original_idea="Edge-first soil moisture monitor",
        completed_stages=["idea_understanding", "solution_landscape", "mutation_engine", "architecture"],
        current_stage="architecture",
    )
    affected = InvalidationManager.invalidate_for_mutation_selection(ctx)
    assert "architecture" in affected
    assert "architecture" not in ctx.completed_stages
    assert "idea_understanding" in ctx.completed_stages


def test_blueprint_exporter():
    blueprint = {
        "executive_summary": "Test Executive Summary",
        "elevator_pitch": "Test Pitch",
        "selected_mutation": "Edge-First",
        "system_architecture_summary": "Modular architecture",
        "execution_strategy": "3 Phase rollout",
        "judge_defense_summary": "Unrivaled defensibility",
    }
    context = {
        "normalized_idea": "Test Project",
        "domain": "Healthcare",
        "target_users": ["Doctors", "Nurses"],
        "technology": {"recommended_stack": {"Frontend": "React", "Backend": "Flask"}},
    }

    md = BlueprintExporter.export_markdown(blueprint, context)
    assert "# Test Project" in md
    assert "Test Executive Summary" in md
    assert "React" in md

    js = BlueprintExporter.export_json(blueprint, context)
    data = json.loads(js)
    assert data["blueprint"]["elevator_pitch"] == "Test Pitch"


def test_assistant_context_and_service():
    ctx = AnalysisContext(
        project_id=1,
        original_idea="Smart Agritech sensor network",
        normalized_idea="Smart Agritech",
        domain="Agriculture",
        problem="Crop yield decline",
        selected_mutation_detail={"title": "Edge AI Sentinel"},
    )
    prompt = AssistantContextBuilder.build_system_context(ctx)
    assert "Smart Agritech" in prompt
    assert "Edge AI Sentinel" in prompt

    assistant = AssistantService()
    reply = assistant.ask(ctx, "How should we deploy the models?")
    assert "response" in reply
    assert len(reply["response"]) > 10


def test_cache_service(app):
    with app.app_context():
        payload = {"problem": "Soil testing delays", "domain": "Agriculture"}
        key = AnalysisCacheService.compute_cache_key("idea_understanding", payload)
        assert "module:idea_understanding" in key and "hash:" in key

        output = {"normalized_idea": "Soil Test Pro"}
        AnalysisCacheService.set("idea_understanding", payload, output, engine="mock")
        cached = AnalysisCacheService.get("idea_understanding", payload)
        assert cached == output


def test_export_and_chat_routes(registered_client, app):
    # Submit an idea through the client
    create_resp = registered_client.post("/idea/new", data={
        "title": "Autonomous Drone Irrigation",
        "idea_text": "Autonomous agricultural drone fleet that detects moisture anomalies using on-device computer vision and micro-sprayers.",
        "language": "en",
    }, follow_redirects=False)
    assert create_resp.status_code == 302
    idea_id = int(create_resp.location.split("/")[-1])

    # 1. Export Markdown
    res_md = registered_client.get(f"/idea/{idea_id}/export/markdown")
    assert res_md.status_code == 200
    assert "text/markdown" in res_md.content_type

    # 2. Export JSON
    res_json = registered_client.get(f"/idea/{idea_id}/export/json")
    assert res_json.status_code == 200
    data = res_json.get_json()
    assert "blueprint" in data

    # 3. Chat with AI Advisor
    res_chat = registered_client.post(
        f"/idea/{idea_id}/chat",
        json={"message": "What is our deployment architecture?"},
    )
    assert res_chat.status_code == 200
    chat_data = res_chat.get_json()
    assert chat_data["status"] == "success"
    assert "reply" in chat_data

    # 4. API Endpoints
    api_bp = registered_client.get(f"/api/projects/{idea_id}/blueprint")
    assert api_bp.status_code == 200
    assert "blueprint" in api_bp.get_json()

    api_chat = registered_client.post(
        f"/api/projects/{idea_id}/chat",
        json={"message": "Summarize defense"},
    )
    assert api_chat.status_code == 200
    assert "reply" in api_chat.get_json()
