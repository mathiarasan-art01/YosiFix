"""Blueprint export: compiles the full 15-stage analysis into a downloadable
Word document using python-docx."""
import io
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def _heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    return h


def build_blueprint_docx(idea, analysis, prompts=None):
    doc = Document()

    title = doc.add_heading(f"YosiFix Master Blueprint: {idea.title}", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    meta = doc.add_paragraph()
    meta.add_run(
        f"Domain: {idea.domain}  |  Innovation Score: {idea.innovation_score}/100  |  "
        f"Engine: {getattr(analysis, 'engine_used', 'groq')}"
    ).italic = True

    # 1. Executive Summary & Problem
    _heading(doc, "1. Executive Summary & Problem Statement")
    blueprint_data = getattr(analysis, "blueprint", {}) or {}
    if blueprint_data.get("elevator_pitch"):
        p = doc.add_paragraph()
        p.add_run(f"Elevator Pitch: \"{blueprint_data['elevator_pitch']}\"").bold = True
    doc.add_paragraph(blueprint_data.get("verified_problem_statement") or idea.raw_text)

    # 2. Empirical Evidence Board
    evidence_data = getattr(analysis, "evidence", {}) or {}
    if evidence_data.get("claims"):
        _heading(doc, "2. Empirical Evidence Board")
        if evidence_data.get("validation_summary"):
            doc.add_paragraph(evidence_data["validation_summary"])
        for c in evidence_data.get("claims", []):
            p = doc.add_paragraph(style="List Bullet")
            status = c.get("verification_status", "verified").upper()
            p.add_run(f"[{status}] {c.get('claim')}: ").bold = True
            p.add_run(f"{c.get('factual_evidence')} (Source: {c.get('source_reference')})")

    # 3. Market Landscape, Similarity & Novelty
    _heading(doc, "3. Market Landscape & Novelty Assessment")
    novelty_data = getattr(analysis, "novelty", {}) or {}
    doc.add_paragraph(
        f"Overall Similarity: {analysis.overall_similarity}%  |  "
        f"Novelty Score: {novelty_data.get('novelty_score', 100 - analysis.overall_similarity)}% "
        f"({novelty_data.get('novelty_tier', 'Evaluated')})"
    )
    if analysis.similarity_verdict:
        doc.add_paragraph(analysis.similarity_verdict)

    for m in analysis.similar_solutions or []:
        p = doc.add_paragraph(style="List Bullet")
        name = m.get("name") or m.get("feature") or "Competitor"
        score = m.get("similarity_score") or m.get("overlap_percentage") or 0
        p.add_run(f"{name} ({score}% overlap): ").bold = True
        p.add_run(m.get("reasoning") or m.get("differentiation_notes") or "")

    # 4. Gaps & Opportunities
    _heading(doc, "4. Gaps & Strategic White Spaces")
    for g in analysis.gap_features or []:
        doc.add_paragraph(str(g), style="List Bullet")

    # 5. Selected Strategic Mutation
    selected_mut = getattr(analysis, "selected_mutation_detail", {}) or {}
    if selected_mut.get("title"):
        _heading(doc, "5. Strategic Pivot / Mutation")
        doc.add_paragraph(f"Active Pivot: {selected_mut.get('title')}", style="Intense Quote")
        doc.add_paragraph(selected_mut.get("rationale", ""))
        for mod in selected_mut.get("key_modifications", []):
            doc.add_paragraph(mod, style="List Bullet")

    # 6. Feasibility & Failure Modes
    reality_data = getattr(analysis, "reality_check", {}) or {}
    failure_data = getattr(analysis, "failures", {}) or {}
    if reality_data or failure_data:
        _heading(doc, "6. Reality Check & Failure Safeguards")
        if reality_data.get("buildability_score"):
            doc.add_paragraph(
                f"Buildability Feasibility Score: {reality_data.get('buildability_score')}% "
                f"({reality_data.get('feasibility_rating', 'Feasible')}) | "
                f"MVP Timeline: {reality_data.get('mvp_complexity_weeks', 4)} weeks"
            )
        if failure_data.get("kill_factor"):
            doc.add_paragraph(f"Critical Vulnerability / Kill Factor: {failure_data['kill_factor']}")
        for f in failure_data.get("failure_modes", []):
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(f"{f.get('scenario_title')} ({f.get('probability')} prob): ").bold = True
            p.add_run(f"Mitigation -> {f.get('mitigation_strategy')}")

    # 7. Recommended Tech Stack & Architecture
    _heading(doc, "7. Technology Stack & Architecture")
    stack = analysis.tech_stack or {}
    if isinstance(stack, dict):
        for k, v in stack.items():
            if k != "trade_offs" and k != "extra_tools":
                doc.add_paragraph(f"{str(k).capitalize()}: {v}")

    # 8. Execution Roadmap
    _heading(doc, "8. Execution Roadmap")
    roadmap = analysis.roadmap or {}
    if isinstance(roadmap, list):
        for phase in roadmap:
            doc.add_heading(f"Phase {phase.get('phase_number', '')}: {phase.get('phase_name', '')} ({phase.get('duration_weeks', 2)} weeks)", level=2)
            for deliv in phase.get("deliverables", []):
                doc.add_paragraph(deliv, style="List Bullet")
    elif isinstance(roadmap, dict):
        for phase_key, phase_label in [("mvp", "MVP (Phase 1)"), ("v2", "Version 2 (Phase 2)"), ("v3", "Version 3 (Phase 3)")]:
            doc.add_heading(phase_label, level=2)
            for item in roadmap.get(phase_key, []):
                doc.add_paragraph(item, style="List Bullet")

    # 9. Judge Attack & Defense
    judge_data = getattr(analysis, "judge_attack", {}) or {}
    if judge_data.get("questions"):
        _heading(doc, "9. Judge Attack Q&A & Pitch Defense")
        for q in judge_data.get("questions", []):
            doc.add_heading(f"[{q.get('category', 'Critique')}] {q.get('question')}", level=2)
            doc.add_paragraph(f"Why Judges Ask: {q.get('why_judges_ask')}")
            doc.add_paragraph(f"Winning Defense: {q.get('model_defense_strategy')}")

    # 10. AI Build Prompt
    if prompts:
        _heading(doc, "10. AI Build Prompt")
        p = doc.add_paragraph()
        run = p.add_run(prompts)
        run.font.name = "Consolas"
        run.font.size = Pt(9)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf
