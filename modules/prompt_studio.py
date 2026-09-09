"""Premium Module: AI Prompt Studio.

Turns the full analysis blueprint into a ready-to-paste master build
prompt, tuned for the quirks of whichever AI coding tool the user
plans to build with. This is the module that converts "we validated
an idea" into "here is exactly what to paste into your coding
assistant to start building it."
"""

TOOL_NOTES = {
    "claude": (
        "Ask for complete, working files in one response rather than fragments. "
        "Request that it flags any assumption it makes explicitly rather than silently guessing."
    ),
    "chatgpt": (
        "Ask it to output full file contents inside clearly labeled code blocks, one per file, "
        "and to summarize the file structure in a tree before the code."
    ),
    "gemini": (
        "Ask it to first restate the plan as a numbered step list, then implement one step at a "
        "time so long responses don't get truncated."
    ),
    "cursor": (
        "Paste this directly into a new Cursor composer/chat with the project folder open, and "
        "ask it to create/edit files directly rather than pasting code back to you."
    ),
    "generic": (
        "Works with any general-purpose coding assistant. Provide it the full context below in one message."
    ),
}


def generate_master_prompt(idea, analysis, target_tool="claude"):
    tool_key = target_tool.lower() if target_tool.lower() in TOOL_NOTES else "generic"
    tool_note = TOOL_NOTES[tool_key]

    gap_lines = "\n".join(f"  - {g}" for g in (analysis.gap_features or [])) or "  - (none identified — focus on execution quality)"
    sdg_lines = "\n".join(
        f"  - SDG {s['sdg_number']}: {s['sdg_name']}" for s in (analysis.sdg_mappings or [])
    ) or "  - (no strong SDG alignment detected)"
    stack = analysis.tech_stack or {}
    extras = ", ".join(stack.get("extra_tools", [])) or "none"
    mvp_lines = "\n".join(f"  {i+1}. {item}" for i, item in enumerate((analysis.roadmap or {}).get("mvp", [])))

    prompt = f"""You are building a project called "{idea.title}".

PROJECT CONTEXT
Domain: {idea.domain}
Problem statement (as given by the founder): {idea.raw_text}

MARKET CONTEXT (already researched — do not re-research from scratch)
Overall similarity to existing solutions: {analysis.overall_similarity}%
Verdict: {analysis.similarity_verdict}

DIFFERENTIATION TARGETS — these are the specific gaps this project must address
that existing solutions in this space do NOT solve well:
{gap_lines}

REAL-WORLD IMPACT ALIGNMENT (for framing/pitch purposes)
{sdg_lines}

REQUIRED TECH STACK
- Frontend: {stack.get('frontend', 'not specified')}
- Backend: {stack.get('backend', 'not specified')}
- Database: {stack.get('database', 'not specified')}
- Additional tools: {extras}

BUILD SCOPE — Phase 1 (MVP) ONLY for this request:
{mvp_lines}

INSTRUCTIONS FOR YOU (the AI coding assistant)
1. Build complete, functional code for every file — no placeholder stubs, no "TODO: implement this".
2. Follow the required tech stack above exactly unless there's a strong technical reason not to (state the reason if you deviate).
3. Bake in the differentiation targets listed above as real, working features — not just comments describing them.
4. Include basic error handling and at least a minimal test for the core feature.
5. If any part of this brief is ambiguous, state your assumption explicitly and proceed — don't stop to ask.

TOOL-SPECIFIC NOTE: {tool_note}
"""
    return prompt.strip()
