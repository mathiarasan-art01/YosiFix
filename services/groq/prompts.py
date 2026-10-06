# services/groq/prompts.py
"""Prompt templates for each stage in the YosiFix AI analysis pipeline.

Every prompt is chained and compact: each stage operates on focused, concise
summaries of previous stages. This prevents token explosion, eliminates 413
'Request too large' errors, and drastically reduces latency and rate limits.
"""

from typing import Dict, Any, Tuple


SYSTEM_ANALYST_ROLE = (
    "You are YosiFix Senior Technical Evaluator & Innovation Architect. "
    "Your mission is to rigorously evaluate project ideas, uncover prior art and market realities, "
    "verify problem claims with empirical facts, identify unexplored gaps, simulate real failure modes, "
    "and design a robust, defensible engineering blueprint. "
    "CRITICAL RULES: "
    "1. You must return ONLY a valid, parseable JSON object matching the requested schema. "
    "2. All numeric values (such as confidence_score, score, relevance, percentages) MUST be strictly numbers (e.g. 0.9, 85, 0.75), NEVER spelled out in words like '0. nine'. "
    "3. Keep each field concise, technical, and directly grounded in the input."
)


def _compact_text(text: Any, max_len: int = 250) -> str:
    if not text:
        return ""
    s = str(text).strip()
    return s[:max_len] + "..." if len(s) > max_len else s


def _compact_list(items: Any, limit: int = 4, max_item_len: int = 80) -> str:
    if not isinstance(items, list):
        return ""
    return ", ".join(_compact_text(it, max_item_len) for it in items[:limit] if it)


def _compact_solutions(solutions: Any, limit: int = 3) -> str:
    if not isinstance(solutions, list):
        return "Standard industry solutions"
    lines = []
    for s in solutions[:limit]:
        if isinstance(s, dict):
            name = s.get("name", "Solution")
            desc = _compact_text(s.get("description", ""), 100)
            lines.append(f"- {name}: {desc}")
    return "\n".join(lines) if lines else "Standard industry solutions"


def _compact_claims(claims: Any, limit: int = 3) -> str:
    if not isinstance(claims, list):
        return "Core operational inefficiencies verified"
    lines = []
    for c in claims[:limit]:
        if isinstance(c, dict):
            claim = _compact_text(c.get("claim", ""), 80)
            status = c.get("verification_status", "verified")
            lines.append(f"- [{status}] {claim}")
    return "\n".join(lines) if lines else "Core operational inefficiencies verified"


def _compact_gaps(gaps: Any, limit: int = 3) -> str:
    if not isinstance(gaps, list):
        return "Edge deployment and localized automation"
    lines = []
    for g in gaps[:limit]:
        if isinstance(g, dict):
            lines.append(f"- {g.get('gap_title', '')}")
    return "\n".join(lines) if lines else "Edge deployment and localized automation"


def _compact_failures(modes: Any, limit: int = 3) -> str:
    if not isinstance(modes, list):
        return "Latency bottlenecks and intermittent connectivity"
    lines = []
    for m in modes[:limit]:
        if isinstance(m, dict):
            lines.append(f"- {m.get('failure_mode', '')}")
    return "\n".join(lines) if lines else "Latency bottlenecks and intermittent connectivity"


def idea_understanding_prompt(raw_text: str) -> Tuple[str, str]:
    cleaned = _compact_text(raw_text, 3500)
    user_prompt = f"""Analyze the following raw project idea. Extract a crisp normalized description, primary target users/personas, high-level domain, core problem statement, domain keywords, key constraints, and essential requirements.

Raw Project Idea:
{cleaned}

Return a valid JSON object matching the IdeaUnderstandingSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def solution_landscape_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Given the verified idea and problem context below, analyze the existing solution landscape.
Identify 3-4 existing tools, commercial products, open-source repositories, or academic baselines that attempt to solve this or similar problems.
Highlight current market trends and research benchmarks.

Context:
- Domain: {context.get('domain')}
- Normalized Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Core Problem: {_compact_text(context.get('problem'), 300)}
- Target Users: {_compact_list(context.get('target_users', []))}
- Keywords: {_compact_list(context.get('keywords', []))}

Return a valid JSON object matching the SolutionLandscapeSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def evidence_board_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    solutions_summary = _compact_solutions(context.get('landscape', {}).get('existing_solutions', []))
    user_prompt = f"""Investigate the factual validity of the claims and problem assumptions in this project.
Categorize each claim as 'verified', 'unverified', or 'disputed'.
Provide empirical evidence, statistics, credible source organizations (e.g. WHO, FAO, IEEE, Gartner, World Bank, peer-reviewed literature), and identify unverified assumptions.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Problem: {_compact_text(context.get('problem'), 300)}
- Domain: {context.get('domain')}
- Existing Landscape:
{solutions_summary}

Return a valid JSON object matching the EvidenceBoardSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def similarity_analysis_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    solutions_summary = _compact_solutions(context.get('landscape', {}).get('existing_solutions', []))
    user_prompt = f"""Compare the user's project against the existing solutions identified in the landscape.
Calculate an overall similarity percentage (0-100%), identify the closest competitor, evaluate feature-by-feature overlap, and provide an objective similarity verdict.

Context:
- Normalized Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Problem: {_compact_text(context.get('problem'), 300)}
- Requirements: {_compact_list(context.get('requirements', []))}
- Existing Solutions:
{solutions_summary}

Return a valid JSON object matching the SimilarityAnalysisSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def novelty_score_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    sim = context.get('similarity', {})
    user_prompt = f"""Assess the true novelty of this project on a 0-100 scale based on evidence and similarity results.
Determine if it is 'Highly Novel', an 'Incremental Improvement', or 'Derivative / Saturated'.
Break down the novelty across technical, workflow, and market dimensions, and highlight the unique value propositions.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Problem: {_compact_text(context.get('problem'), 300)}
- Similarity Score: {sim.get('overall_similarity_score', 60)}%
- Similarity Verdict: {sim.get('similarity_verdict', 'Moderate Overlap')}
- Closest Competitor: {sim.get('closest_competitor', 'Existing Industry Platform')}

Return a valid JSON object matching the NoveltyScoreSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def research_gap_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    solutions_summary = _compact_solutions(context.get('landscape', {}).get('existing_solutions', []))
    novelty = context.get('novelty', {})
    user_prompt = f"""Identify the critical white spaces and unexplored gaps between existing solutions and unmet user needs.
Identify technical white spaces (e.g. offline execution, lightweight models, multimodal integration, privacy-preserving techniques) and market gaps.
Recommend specific high-leverage angles to capture these gaps.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Problem: {_compact_text(context.get('problem'), 300)}
- Prior Art:
{solutions_summary}
- Novelty Evaluation: Score {novelty.get('overall_novelty_score', 70)}%, Verdict: {novelty.get('novelty_verdict', 'Differentiated')}

Return a valid JSON object matching the ResearchGapSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def mutation_engine_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    gaps_summary = _compact_gaps(context.get('gaps', {}).get('white_spaces', []))
    user_prompt = f"""Generate 3 to 4 distinct, transformative architectural/strategic mutations for this project.
Each mutation must take this project from a standard idea into an exceptional, highly defensible solution.
Examples of mutation paradigms:
- 'edge_offline': On-device inference, zero-bandwidth fallback, edge computing
- 'privacy_first': Zero-knowledge proofs, federated learning, local cryptographic storage
- 'low_cost_hardware': Microcontroller / sensor IoT integration, ultra-low bill of materials
- 'agentic_workflow': Multi-agent autonomous verification, human-in-the-loop validation
- 'community_driven': Decentralized crowdsourced verification, localized data collection

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Problem: {_compact_text(context.get('problem'), 300)}
- Key Unaddressed Gaps:
{gaps_summary}

Return a valid JSON object matching the MutationEngineSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def reality_check_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    selected_mutation = context.get('selected_mutation_detail', {})
    user_prompt = f"""Perform a rigorous reality check and technical feasibility analysis.
Assess prerequisites (APIs, developer skills, datasets, hardware), regulatory/compliance hurdles (GDPR, HIPAA, liability), and assign a 0-100 buildability score.
Estimate realistic MVP timeline in weeks for a focused team of 2-3 engineers.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Core Problem: {_compact_text(context.get('problem'), 300)}
- Selected Mutation / Direction: {selected_mutation.get('title', 'Core System Pivot')}
- Mutation Rationale: {_compact_text(selected_mutation.get('rationale', ''), 150)}
- Requirements: {_compact_list(context.get('requirements', []))}
- Constraints: {_compact_list(context.get('constraints', []))}

Return a valid JSON object matching the RealityCheckSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def failure_simulation_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    selected_mutation = context.get('selected_mutation_detail', {})
    reality = context.get('reality_check', {})
    user_prompt = f"""Simulate the top 3-4 most probable real-world failure modes for this project.
Consider data starvation, latency bottlenecks, operational unit economics, user adoption inertia, and critical single points of failure.
Identify the single lethal 'kill factor' and specify concrete architectural mitigations.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Problem: {_compact_text(context.get('problem'), 300)}
- Selected Mutation: {selected_mutation.get('title', 'Target Architecture')}
- Buildability Score: {reality.get('buildability_score', 80)}/100
- Regulatory Constraints: {_compact_list(reality.get('regulatory_and_compliance_hurdles', []))}

Return a valid JSON object matching the FailureSimulationSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def impact_and_sdg_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    claims_summary = _compact_claims(context.get('evidence', {}).get('claims', []))
    user_prompt = f"""Map the project's genuine real-world impact and align with UN Sustainable Development Goals (SDGs).
Specify exact SDG numbers, official target numbers (e.g. Target 2.4, Target 3.8), verifiable quantifiable impact metrics, and expected beneficiary reach.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Domain: {context.get('domain')}
- Target Users: {_compact_list(context.get('target_users', []))}
- Verified Evidence Grounding:
{claims_summary}

Return a valid JSON object matching the ImpactAndSDGSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def technology_decision_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    selected_mutation = context.get('selected_mutation_detail', {})
    user_prompt = f"""Recommend the optimal production technology stack for this project.
For each layer (Frontend, Backend, Database, AI/ML, Cloud/Infra), detail the selected technology, the alternative considered, and a rigorous engineering justification for why the chosen tech wins and why the alternative was rejected.
State the overarching architectural pattern.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Domain: {context.get('domain')}
- Technical Direction: {selected_mutation.get('title', 'Modular System')}
- Requirements: {_compact_list(context.get('requirements', []))}
- Technical Constraints: {_compact_list(context.get('constraints', []))}

Return a valid JSON object matching the TechnologyDecisionSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def architecture_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    tech = context.get('technology', {})
    fe = tech.get('frontend', {}).get('selected', 'React / Next.js') if isinstance(tech.get('frontend'), dict) else 'Web'
    be = tech.get('backend', {}).get('selected', 'FastAPI / Python') if isinstance(tech.get('backend'), dict) else 'API'
    db_tech = tech.get('database', {}).get('selected', 'PostgreSQL / SQLite') if isinstance(tech.get('database'), dict) else 'Database'
    pattern = tech.get('architecture_pattern', 'Layered Modular')

    user_prompt = f"""Design the system architecture and generate valid Mermaid.js diagram syntax (flowchart TD or graph TD).
Break down all major subsystems, their responsibilities, exact technologies, and dependencies.
Describe the complete end-to-end data flow.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Architecture Pattern: {pattern}
- Core Components: Frontend ({fe}), Backend ({be}), Database ({db_tech})
- Selected Strategy: {context.get('selected_mutation_detail', {}).get('title', 'Resilient Edge Design')}

Ensure the Mermaid diagram syntax is strictly valid and enclosed cleanly without broken brackets or syntax errors.
Return a valid JSON object matching the ArchitectureSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def roadmap_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    reality = context.get('reality_check', {})
    failures = context.get('failures', {})
    user_prompt = f"""Construct an execution roadmap with 3-4 structured phases.
For each phase, specify duration in weeks, concrete testable deliverables, and key risks.
Define the unambiguous MVP milestone criteria and critical path dependencies.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- MVP Duration Target: {reality.get('estimated_mvp_weeks', 6)} weeks
- Critical Failure to Defend Against: {_compact_text(failures.get('kill_factor', 'System latency'), 150)}
- High-level Pattern: {context.get('technology', {}).get('architecture_pattern', 'Micro-modular')}

Return a valid JSON object matching the RoadmapSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def judge_attack_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    gaps_summary = _compact_gaps(context.get('gaps', {}).get('white_spaces', []))
    failures_summary = _compact_failures(context.get('failures', {}).get('failure_modes', []))
    user_prompt = f"""Simulate an intense Q&A interrogation by top hackathon judges, technical lead architects, and venture investors.
Generate 4-6 tough questions spanning technical defensibility, business viability, scalability limitations, and unit economics.
For each question, explain why judges ask it, formulate a winning model defense strategy with concrete evidence to cite, and supply talking points.

Context:
- Idea: {_compact_text(context.get('normalized_idea'), 300)}
- Novelty Verdict: {context.get('novelty', {}).get('novelty_verdict', 'Novel Solution')}
- Strategic Pivot: {context.get('selected_mutation_detail', {}).get('title', 'Optimized Workflow')}
- White Spaces Captured:
{gaps_summary}
- Identified System Risks:
{failures_summary}

Return a valid JSON object matching the JudgeAttackSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def judge_evaluate_prompt(question: str, user_answer: str, context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Evaluate the user's defense answer to a critical judge question.
Grade the response (Score 0-100), identify strong points, highlight missing technical defenses or vulnerabilities, and provide an upgraded, polished rebuttal.

Context:
- Project: {_compact_text(context.get('normalized_idea'), 300)}
- Question: {_compact_text(question, 200)}
- User's Answer: {_compact_text(user_answer, 500)}

Return a valid JSON object with fields:
{{
  "score": float,
  "verdict": "Strong Defense" | "Adequate but Incomplete" | "Weak / Vulnerable",
  "strengths": list of str,
  "critique": str,
  "upgraded_rebuttal": str
}}
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def master_blueprint_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    tech = context.get('technology', {})
    fe = tech.get('frontend', {}).get('selected', 'Web App') if isinstance(tech.get('frontend'), dict) else 'Web'
    be = tech.get('backend', {}).get('selected', 'API Backend') if isinstance(tech.get('backend'), dict) else 'API'
    db_tech = tech.get('database', {}).get('selected', 'DB') if isinstance(tech.get('database'), dict) else 'DB'

    user_prompt = f"""Synthesize all previous verified outputs into an authoritative Master Project Blueprint.
Include an executive summary, verified problem statement, validated target audience, core innovation claim & gap captured, chosen mutation details, architecture summary, MVP execution strategy, a high-converting 30-second elevator pitch, and judge defense summary.

Synthesized Decision State:
- Project: {_compact_text(context.get('normalized_idea'), 300)}
- Domain & Problem: {_compact_text(context.get('problem'), 300)}
- Target Personas: {_compact_list(context.get('target_users', []))}
- Selected Innovation: {context.get('selected_mutation_detail', {}).get('title', 'Edge-first intelligence')}
- Defensibility / Differentiator: {_compact_list(context.get('novelty', {}).get('unique_value_props', []))}
- Approved Tech Stack: {fe} (Frontend) + {be} (Backend) + {db_tech} (Storage)
- MVP Timeline: {context.get('reality_check', {}).get('estimated_mvp_weeks', 6)} weeks
- Critical Failure Mitigation: {_compact_text(context.get('failures', {}).get('kill_factor', 'Offline fallback'), 150)}

Return a valid JSON object matching the MasterBlueprintSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt
