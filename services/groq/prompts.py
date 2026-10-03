# services/groq/prompts.py
"""Prompt templates for each stage in the YosiFix AI analysis pipeline.

Every prompt is chained: it takes the accumulated AnalysisContext so that
each stage operates strictly from the verified outputs of previous stages,
producing grounded, interconnected, and evidence-driven analysis.
"""

from typing import Dict, Any, Tuple


SYSTEM_ANALYST_ROLE = (
    "You are YosiFix Senior Technical Evaluator & Innovation Architect. "
    "Your mission is to rigorously evaluate project ideas, uncover prior art and market realities, "
    "verify problem claims with empirical facts, identify unexplored gaps, simulate real failure modes, "
    "and design a robust, defensible engineering blueprint. "
    "Do not produce generic AI praise or disconnected fluff. Be critical, technically precise, and evidence-driven. "
    "You must return ONLY a valid JSON object matching the requested schema."
)


def idea_understanding_prompt(raw_text: str) -> Tuple[str, str]:
    user_prompt = f"""Analyze the following raw project idea. Extract a crisp normalized description, primary target users/personas, high-level domain, core problem statement, domain keywords, key constraints, and essential requirements.

Raw Project Idea:
{raw_text}

Return a valid JSON object matching the IdeaUnderstandingSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def solution_landscape_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Given the verified idea and problem context below, analyze the existing solution landscape.
Identify 3-5 existing tools, commercial products, open-source repositories, or academic baselines that attempt to solve this or similar problems.
Highlight current market trends and research benchmarks.

Context:
- Domain: {context.get('domain')}
- Normalized Idea: {context.get('normalized_idea')}
- Core Problem: {context.get('problem')}
- Target Users: {', '.join(context.get('target_users', []))}
- Keywords: {', '.join(context.get('keywords', []))}

Return a valid JSON object matching the SolutionLandscapeSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def evidence_board_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Investigate the factual validity of the claims and problem assumptions in this project.
Categorize each claim as 'verified', 'unverified', or 'disputed'.
Provide empirical evidence, statistics, credible source organizations (e.g. WHO, FAO, IEEE, Gartner, World Bank, peer-reviewed literature), and identify unverified assumptions.

Context:
- Idea: {context.get('normalized_idea')}
- Problem: {context.get('problem')}
- Domain: {context.get('domain')}
- Existing Landscape: {context.get('landscape', {})}

Return a valid JSON object matching the EvidenceBoardSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def similarity_analysis_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Compare the user's project against the existing solutions identified in the landscape.
Calculate an overall similarity percentage (0-100%), identify the closest competitor, evaluate feature-by-feature overlap, and provide an objective similarity verdict.

Context:
- Normalized Idea: {context.get('normalized_idea')}
- Problem: {context.get('problem')}
- Requirements: {context.get('requirements', [])}
- Existing Solutions: {context.get('landscape', {}).get('existing_solutions', [])}

Return a valid JSON object matching the SimilarityAnalysisSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def novelty_score_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Assess the true novelty of this project on a 0-100 scale based on evidence and similarity results.
Determine if it is 'Highly Novel', an 'Incremental Improvement', or 'Derivative / Saturated'.
Break down the novelty across technical, workflow, and market dimensions, and highlight the unique value propositions.

Context:
- Idea: {context.get('normalized_idea')}
- Problem: {context.get('problem')}
- Similarity Score: {context.get('similarity', {}).get('overall_similarity_score')}%
- Similarity Verdict: {context.get('similarity', {}).get('similarity_verdict')}
- Closest Competitor: {context.get('similarity', {}).get('closest_competitor')}
- Existing Solutions: {context.get('landscape', {}).get('existing_solutions', [])}

Return a valid JSON object matching the NoveltyScoreSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def research_gap_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Identify the critical white spaces and unexplored gaps between existing solutions and unmet user needs.
Identify technical white spaces (e.g. offline execution, lightweight models, multimodal integration, privacy-preserving techniques) and market gaps.
Recommend specific high-leverage angles to capture these gaps.

Context:
- Idea: {context.get('normalized_idea')}
- Problem: {context.get('problem')}
- Existing Solutions: {context.get('landscape', {}).get('existing_solutions', [])}
- Overlap & Similarity: {context.get('similarity', {})}
- Novelty Analysis: {context.get('novelty', {})}

Return a valid JSON object matching the ResearchGapSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def mutation_engine_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Generate 3 to 4 distinct, transformative architectural/strategic mutations for this project.
Each mutation must take this project from a standard idea into an exceptional, highly defensible solution.
Examples of mutation paradigms:
- 'edge_offline': On-device inference, zero-bandwidth fallback, edge computing
- 'privacy_first': Zero-knowledge proofs, federated learning, local cryptographic storage
- 'low_cost_hardware': Microcontroller / sensor IoT integration, ultra-low bill of materials
- 'agentic_workflow': Multi-agent autonomous verification, human-in-the-loop validation
- 'community_driven': Decentralized crowdsourced verification, localized data collection

Context:
- Idea: {context.get('normalized_idea')}
- Problem: {context.get('problem')}
- Gaps: {context.get('gaps', {})}
- Novelty: {context.get('novelty', {})}

Return a valid JSON object matching the MutationEngineSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def reality_check_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    selected_mutation = context.get('selected_mutation_detail', {})
    user_prompt = f"""Perform a rigorous reality check and technical feasibility analysis.
Assess prerequisites (APIs, developer skills, datasets, hardware), regulatory/compliance hurdles (GDPR, HIPAA, liability), and assign a 0-100 buildability score.
Estimate realistic MVP timeline in weeks for a focused team of 2-3 engineers.

Context:
- Idea: {context.get('normalized_idea')}
- Core Problem: {context.get('problem')}
- Selected Mutation / Direction: {selected_mutation.get('title', 'Default Path')}
- Requirements: {context.get('requirements', [])}
- Constraints: {context.get('constraints', [])}

Return a valid JSON object matching the RealityCheckSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def failure_simulation_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Simulate the top 3-5 most probable real-world failure modes for this project.
Consider data starvation, latency bottlenecks, operational unit economics, user adoption inertia, and critical single points of failure.
Identify the single lethal 'kill factor' and specify concrete architectural mitigations.

Context:
- Idea: {context.get('normalized_idea')}
- Problem: {context.get('problem')}
- Feasibility: {context.get('reality_check', {})}
- Selected Mutation: {context.get('selected_mutation_detail', {})}

Return a valid JSON object matching the FailureSimulationSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def impact_and_sdg_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Map the project's genuine real-world impact and align with UN Sustainable Development Goals (SDGs).
Specify exact SDG numbers, official target numbers (e.g. Target 2.4, Target 3.8), verifiable quantifiable impact metrics, and expected beneficiary reach.

Context:
- Idea: {context.get('normalized_idea')}
- Problem: {context.get('problem')}
- Target Users: {context.get('target_users', [])}
- Evidence Base: {context.get('evidence', {})}

Return a valid JSON object matching the ImpactAndSDGSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def technology_decision_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Recommend the optimal production technology stack for this project.
For each layer (Frontend, Backend, Database, AI/ML, Cloud/Infra), detail the selected technology, the alternative considered, and a rigorous engineering justification for why the chosen tech wins and why the alternative was rejected.
State the overarching architectural pattern.

Context:
- Idea: {context.get('normalized_idea')}
- Domain: {context.get('domain')}
- Feasibility & Hardware: {context.get('reality_check', {})}
- Mutation: {context.get('selected_mutation_detail', {})}

Return a valid JSON object matching the TechnologyDecisionSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def architecture_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Design the system architecture and generate valid Mermaid.js diagram syntax (flowchart TD or graph TD).
Break down all major subsystems, their responsibilities, exact technologies, and dependencies.
Describe the complete end-to-end data flow.

Context:
- Idea: {context.get('normalized_idea')}
- Stack: {context.get('technology', {})}
- Pattern: {context.get('technology', {}).get('architecture_pattern')}
- Selected Mutation: {context.get('selected_mutation_detail', {})}

Ensure the Mermaid diagram syntax is strictly valid and enclosed cleanly without broken brackets or syntax errors.
Return a valid JSON object matching the ArchitectureSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def roadmap_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Construct an execution roadmap with 3-4 structured phases.
For each phase, specify duration in weeks, concrete testable deliverables, and key risks.
Define the unambiguous MVP milestone criteria and critical path dependencies.

Context:
- Idea: {context.get('normalized_idea')}
- Feasibility: {context.get('reality_check', {})}
- Architecture: {context.get('architecture', {})}
- Failure Mitigations: {context.get('failures', {})}

Return a valid JSON object matching the RoadmapSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def judge_attack_prompt(context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Simulate an intense Q&A interrogation by top hackathon judges, technical lead architects, and venture investors.
Generate 4-6 tough questions spanning technical defensibility, business viability, scalability limitations, and unit economics.
For each question, explain why judges ask it, formulate a winning model defense strategy with concrete evidence to cite, and supply talking points.

Context:
- Idea: {context.get('normalized_idea')}
- Novelty: {context.get('novelty', {})}
- Gaps: {context.get('gaps', {})}
- Feasibility: {context.get('reality_check', {})}
- Failures: {context.get('failures', {})}
- Architecture: {context.get('architecture', {})}

Return a valid JSON object matching the JudgeAttackSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt


def judge_evaluate_prompt(question: str, user_answer: str, context: Dict[str, Any]) -> Tuple[str, str]:
    user_prompt = f"""Evaluate the user's defense answer to a critical judge question.
Grade the response (Score 0-100), identify strong points, highlight missing technical defenses or vulnerabilities, and provide an upgraded, polished rebuttal.

Context:
- Project: {context.get('normalized_idea')}
- Question: {question}
- User's Answer: {user_answer}

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
    user_prompt = f"""Synthesize all previous verified outputs into an authoritative Master Project Blueprint.
Include an executive summary, verified problem statement, validated target audience, core innovation claim & gap captured, chosen mutation details, architecture summary, MVP execution strategy, a high-converting 30-second elevator pitch, and judge defense summary.

Context:
- Idea: {context.get('normalized_idea')}
- Problem: {context.get('problem')}
- Evidence: {context.get('evidence', {})}
- Novelty: {context.get('novelty', {})}
- Gaps: {context.get('gaps', {})}
- Mutation: {context.get('selected_mutation_detail', {})}
- Tech Stack: {context.get('technology', {})}
- Roadmap: {context.get('roadmap', {})}
- Judge Attack: {context.get('judge_attack', {})}

Return a valid JSON object matching the MasterBlueprintSchema.
"""
    return SYSTEM_ANALYST_ROLE, user_prompt
