import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.classifier import classify_idea_rule_based
from modules.knowledge_base import get_domain_entries, get_all_domains
from modules.similarity import analyze_similarity
from modules.gap_analysis import detect_gaps, compute_innovation_score
from modules.sdg_mapper import map_sdgs
from modules.tech_recommender import recommend_stack
from modules.architecture import generate_architecture_diagram
from modules.roadmap import generate_roadmap
from modules.prompt_studio import generate_master_prompt
from modules.i18n import t


FARMER_IDEA = (
    "A mobile app that helps farmers detect crop disease early using photos "
    "taken on their phone, and connects them to nearby agri-input suppliers."
)


def test_classifier_detects_agriculture():
    result = classify_idea_rule_based(FARMER_IDEA)
    assert result["domain"] == "Agriculture"
    assert result["confidence"] > 0
    assert result["engine"] == "rule-based"


def test_classifier_handles_empty_text():
    result = classify_idea_rule_based("")
    assert result["domain"] == "General / Other"


def test_knowledge_base_has_all_domains_populated():
    domains = get_all_domains()
    assert len(domains) >= 10
    for d in domains:
        assert len(get_domain_entries(d)) >= 3


def test_similarity_analysis_returns_ranked_matches():
    result = analyze_similarity(FARMER_IDEA, "Agriculture")
    assert len(result["matches"]) > 0
    scores = [m["similarity_score"] for m in result["matches"]]
    assert scores == sorted(scores, reverse=True)
    assert 0 <= result["overall_similarity"] <= 100


def test_similarity_unknown_domain_returns_empty_gracefully():
    result = analyze_similarity("some idea", "Nonexistent Domain")
    assert result["matches"] == []
    assert result["overall_similarity"] == 0.0


def test_gap_detection_produces_opportunities():
    sim = analyze_similarity(FARMER_IDEA, "Agriculture")
    gaps = detect_gaps(FARMER_IDEA, sim["matches"])
    assert isinstance(gaps["gap_features"], list)
    assert isinstance(gaps["opportunity_notes"], list)
    assert len(gaps["opportunity_notes"]) > 0


def test_innovation_score_bounds():
    score = compute_innovation_score(overall_similarity=80, gap_count=1, sdg_count=1)
    assert 5 <= score <= 100
    score2 = compute_innovation_score(overall_similarity=10, gap_count=5, sdg_count=3)
    assert score2 > score  # lower overlap + more gaps/impact should score higher


def test_sdg_mapping_detects_agriculture_and_hunger():
    results = map_sdgs(FARMER_IDEA)
    numbers = [r["sdg_number"] for r in results]
    assert 2 in numbers  # Zero Hunger (agriculture keyword)


def test_sdg_mapping_no_match_returns_empty():
    results = map_sdgs("a generic app with no thematic keywords at all xyz")
    assert isinstance(results, list)


def test_tech_recommender_defaults_to_lean_stack():
    stack = recommend_stack(FARMER_IDEA, "Agriculture")
    assert "Flask" in stack["backend"]
    assert isinstance(stack["extra_tools"], list)


def test_tech_recommender_detects_image_and_ai_signals():
    stack = recommend_stack(FARMER_IDEA, "Agriculture")
    joined = " ".join(stack["extra_tools"]).lower()
    assert "vision" in joined or "opencv" in joined


def test_architecture_diagram_is_valid_mermaid_flowchart():
    stack = recommend_stack(FARMER_IDEA, "Agriculture")
    diagram = generate_architecture_diagram(stack, "Agriculture")
    assert diagram.startswith("flowchart TD")
    assert "-->" in diagram


def test_roadmap_has_three_phases_with_items():
    stack = recommend_stack(FARMER_IDEA, "Agriculture")
    roadmap = generate_roadmap(["gap one", "gap two"], stack)
    assert len(roadmap["mvp"]) > 0
    assert len(roadmap["v2"]) > 0
    assert len(roadmap["v3"]) > 0


def test_i18n_returns_translated_strings():
    assert t("nav_dashboard", "en") == "Dashboard"
    assert t("nav_dashboard", "ta") != t("nav_dashboard", "en")
    assert t("nav_dashboard", "hi") != t("nav_dashboard", "en")
    assert t("nonexistent_key", "en") == "nonexistent_key"


class _FakeIdea:
    title = "CropGuard"
    domain = "Agriculture"
    raw_text = FARMER_IDEA


class _FakeAnalysis:
    overall_similarity = 42.0
    similarity_verdict = "Moderate overlap"
    gap_features = ["no offline mode", "no market linkage"]
    sdg_mappings = [{"sdg_number": 2, "sdg_name": "Zero Hunger"}]
    tech_stack = {"frontend": "PWA", "backend": "Flask", "database": "SQLite", "extra_tools": ["OpenCV"]}
    roadmap = {"mvp": ["Build core detection flow"], "v2": [], "v3": []}


def test_prompt_studio_generates_nonempty_prompt_for_each_tool():
    for tool in ["claude", "chatgpt", "gemini", "cursor", "generic"]:
        prompt = generate_master_prompt(_FakeIdea(), _FakeAnalysis(), target_tool=tool)
        assert len(prompt) > 100
        assert "CropGuard" in prompt
        assert "no offline mode" in prompt
