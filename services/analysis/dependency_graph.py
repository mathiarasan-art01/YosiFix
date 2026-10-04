"""Dependency Graph for YosiFix 15-Stage Analysis Pipeline.

Maps upstream and downstream dependencies for every stage, enabling intelligent
recalculation and selective invalidation when user inputs or selections change.
"""
from typing import List, Dict, Set

# Full 15-stage pipeline in strict execution sequence
PIPELINE_STAGES = [
    "idea_understanding",     # Stage 1: Problem, audience, keywords
    "solution_landscape",     # Stage 2: Categories, existing paradigms
    "evidence_board",         # Stage 3: Multi-channel empirical validation
    "similarity_analysis",    # Stage 4: Overlap with existing solutions
    "novelty_score",          # Stage 5: Differentiation & novelty score
    "research_gap",           # Stage 6: Unmet needs & white spaces
    "mutation_engine",        # Stage 7: Strategic pivot hypotheses
    "reality_check",          # Stage 8: Buildability, team constraints, MVP
    "failure_simulation",     # Stage 9: Risk factors, failure modes, mitigations
    "impact_and_sdg",         # Stage 10: UN SDGs, societal impact metrics
    "technology_decision",    # Stage 11: Stack recommendations & trade-offs
    "architecture",           # Stage 12: System architecture & Mermaid flow
    "roadmap",                # Stage 13: Phase-wise execution timeline
    "judge_attack",           # Stage 14: Defense simulation & investor Q&A
    "master_blueprint",       # Stage 15: Unified project specification
]

STAGE_METADATA = {
    "idea_understanding": {
        "title": "Idea Understanding",
        "description": "Deconstructs problem statement, target audience, and core constraints.",
        "icon": "brain",
    },
    "solution_landscape": {
        "title": "Solution Landscape",
        "description": "Categorizes existing market and academic solution paradigms.",
        "icon": "map",
    },
    "evidence_board": {
        "title": "Empirical Evidence Board",
        "description": "Collects multi-source empirical validation across code, papers, and products.",
        "icon": "search",
    },
    "similarity_analysis": {
        "title": "Similarity Analysis",
        "description": "Calculates dimensional overlap and competitor match scores.",
        "icon": "copy",
    },
    "novelty_score": {
        "title": "Novelty & Defensibility",
        "description": "Quantifies uniqueness score and defensibility moat.",
        "icon": "award",
    },
    "research_gap": {
        "title": "Research & Market Gaps",
        "description": "Identifies unexplored white spaces and unmet market demands.",
        "icon": "target",
    },
    "mutation_engine": {
        "title": "Strategic Mutation Engine",
        "description": "Formulates architectural and business pivots to escape saturated markets.",
        "icon": "shuffle",
    },
    "reality_check": {
        "title": "Feasibility & Reality Check",
        "description": "Assesses technical buildability, MVP timelines, and resource limits.",
        "icon": "check-circle",
    },
    "failure_simulation": {
        "title": "Failure Mode Simulation",
        "description": "Stress-tests edge cases, adoption blockers, and single-point-of-failure risks.",
        "icon": "alert-triangle",
    },
    "impact_and_sdg": {
        "title": "Impact & UN SDG Alignment",
        "description": "Maps societal impact against United Nations Sustainable Development Goals.",
        "icon": "globe",
    },
    "technology_decision": {
        "title": "Technology Decision Matrix",
        "description": "Selects optimal frameworks, databases, and deployment runtimes.",
        "icon": "cpu",
    },
    "architecture": {
        "title": "System Architecture",
        "description": "Generates production data flows and interactive Mermaid diagrams.",
        "icon": "layers",
    },
    "roadmap": {
        "title": "Phased Execution Roadmap",
        "description": "Breaks MVP and scaling delivery into milestones and deliverables.",
        "icon": "calendar",
    },
    "judge_attack": {
        "title": "Judge & Investor Attack Lab",
        "description": "Simulates rigorous hackathon judge scrutiny and hostile defense queries.",
        "icon": "shield",
    },
    "master_blueprint": {
        "title": "Master Project Blueprint",
        "description": "Synthesizes all 15 stages into an authoritative, investor-grade specification.",
        "icon": "file-text",
    },
}

# Immediate prerequisites for each stage
STAGE_DEPENDENCIES: Dict[str, List[str]] = {
    "idea_understanding": [],
    "solution_landscape": ["idea_understanding"],
    "evidence_board": ["idea_understanding", "solution_landscape"],
    "similarity_analysis": ["solution_landscape", "evidence_board"],
    "novelty_score": ["similarity_analysis"],
    "research_gap": ["solution_landscape", "novelty_score"],
    "mutation_engine": ["research_gap", "novelty_score"],
    "reality_check": ["mutation_engine", "idea_understanding"],
    "failure_simulation": ["reality_check", "mutation_engine"],
    "impact_and_sdg": ["idea_understanding", "mutation_engine"],
    "technology_decision": ["mutation_engine", "reality_check"],
    "architecture": ["technology_decision", "mutation_engine"],
    "roadmap": ["architecture", "reality_check"],
    "judge_attack": ["architecture", "failure_simulation", "novelty_score"],
    "master_blueprint": [
        "idea_understanding",
        "mutation_engine",
        "reality_check",
        "technology_decision",
        "architecture",
        "roadmap",
        "judge_attack",
    ],
}


class DependencyGraph:
    """Provides dependency traversal and downstream invalidation lookup."""

    @staticmethod
    def get_stage_order() -> List[str]:
        return list(PIPELINE_STAGES)

    @staticmethod
    def get_prerequisites(stage: str) -> List[str]:
        return STAGE_DEPENDENCIES.get(stage, [])

    @staticmethod
    def get_downstream_stages(changed_stage: str) -> List[str]:
        """Return all stages that directly or transitively depend on changed_stage."""
        if changed_stage not in PIPELINE_STAGES:
            return []

        downstream: Set[str] = set()
        queue = [changed_stage]

        while queue:
            current = queue.pop(0)
            for stage, prereqs in STAGE_DEPENDENCIES.items():
                if current in prereqs and stage not in downstream:
                    downstream.add(stage)
                    queue.append(stage)

        # Return downstream stages in topological execution order
        return [s for s in PIPELINE_STAGES if s in downstream]

    @staticmethod
    def get_stages_affected_by_mutation() -> List[str]:
        """Convenience method returning stages influenced by choosing a mutation."""
        return DependencyGraph.get_downstream_stages("mutation_engine")
