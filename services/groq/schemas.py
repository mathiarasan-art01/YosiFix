# services/groq/schemas.py
"""Pydantic schemas describing the structured JSON contracts for every stage
in the YosiFix AI analysis pipeline.

Every module in the pipeline operates on structured data that adheres to these schemas.
Compatible with both Pydantic v1 and v2.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Helper Base Model supporting both v1 and v2 methods
# ---------------------------------------------------------------------------
class PipelineBaseSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"

    def to_dict(self) -> Dict[str, Any]:
        if hasattr(self, "model_dump"):
            return self.model_dump()
        return self.dict()

    @classmethod
    def get_json_schema(cls) -> Dict[str, Any]:
        if hasattr(cls, "model_json_schema"):
            return cls.model_json_schema()
        return cls.schema()


# ---------------------------------------------------------------------------
# 1. Idea Understanding
# ---------------------------------------------------------------------------
class IdeaUnderstandingSchema(PipelineBaseSchema):
    normalized_idea: str = Field(..., description="Concise, precise technical summary of the core idea")
    target_users: List[str] = Field(default_factory=list, description="Primary user personas or beneficiaries")
    domain: str = Field(..., description="High-level domain (e.g. Agriculture, Healthcare, FinTech, EdTech)")
    problem: str = Field(..., description="The fundamental pain point or problem statement")
    keywords: List[str] = Field(default_factory=list, description="Key domain concepts and technical keywords")
    constraints: List[str] = Field(default_factory=list, description="Known operational, technical, or domain constraints")
    requirements: List[str] = Field(default_factory=list, description="Core requirements or must-have capabilities")


# ---------------------------------------------------------------------------
# 2. Solution Landscape
# ---------------------------------------------------------------------------
class ExistingSolutionSchema(PipelineBaseSchema):
    name: str = Field(..., description="Name of the existing product, project, or paper")
    category: str = Field(..., description="Category: Commercial, Open Source, Academic Paper, or Startup")
    description: str = Field(..., description="What this solution does")
    strengths: List[str] = Field(default_factory=list, description="Notable strengths")
    limitations: List[str] = Field(default_factory=list, description="Key limitations or flaws")
    url_or_reference: Optional[str] = Field(None, description="Reference link or organization")


class SolutionLandscapeSchema(PipelineBaseSchema):
    existing_solutions: List[ExistingSolutionSchema] = Field(default_factory=list, description="Comparable solutions in market or research")
    market_trends: List[str] = Field(default_factory=list, description="Current macro trends impacting this domain")
    research_benchmarks: List[str] = Field(default_factory=list, description="State of the art benchmarks or baselines")


# ---------------------------------------------------------------------------
# 3. Evidence Board
# ---------------------------------------------------------------------------
class ClaimEvidenceSchema(PipelineBaseSchema):
    claim: str = Field(..., description="Specific claim made about the problem or market need")
    verification_status: str = Field(..., description="'verified', 'unverified', or 'disputed'")
    factual_evidence: str = Field(..., description="Factual basis, statistics, or documented evidence")
    source_reference: str = Field(..., description="Credible source, organization, or data reference")
    confidence_score: float = Field(default=0.8, description="Confidence in this verification (0.0 to 1.0)")


class EvidenceBoardSchema(PipelineBaseSchema):
    claims: List[ClaimEvidenceSchema] = Field(default_factory=list, description="List of verified/unverified problem claims")
    unverified_assumptions: List[str] = Field(default_factory=list, description="Risky assumptions that need customer validation")
    validation_summary: str = Field(default="", description="Overall assessment: is the problem real and verified?")


# ---------------------------------------------------------------------------
# 4. Similarity Analysis
# ---------------------------------------------------------------------------
class FeatureOverlapSchema(PipelineBaseSchema):
    feature: str = Field(..., description="Feature or capability examined")
    overlap_percentage: float = Field(..., description="Percentage overlap with existing tools (0-100)")
    matched_with: str = Field(..., description="Existing tool or benchmark it overlaps with")
    differentiation_notes: str = Field(..., description="How the user's idea differs or fails to differ")


class SimilarityAnalysisSchema(PipelineBaseSchema):
    overall_similarity_score: float = Field(..., description="Overall similarity index from 0 to 100")
    similarity_verdict: str = Field(..., description="Verdict e.g. High Overlap, Moderate Differentiation, Highly Unique")
    closest_competitor: str = Field(..., description="The closest existing alternative")
    feature_overlap: List[FeatureOverlapSchema] = Field(default_factory=list, description="Breakdown of feature overlaps")


# ---------------------------------------------------------------------------
# 5. Novelty Assessment
# ---------------------------------------------------------------------------
class NoveltyScoreSchema(PipelineBaseSchema):
    novelty_score: float = Field(..., description="Novelty rating from 0 to 100")
    novelty_tier: str = Field(..., description="'Highly Novel', 'Incremental Improvement', or 'Derivative / Saturated'")
    unique_value_props: List[str] = Field(default_factory=list, description="Key aspects that make this idea unique")
    novelty_breakdown: Dict[str, float] = Field(default_factory=dict, description="Component scores e.g. technical, workflow, market")
    novelty_rationale: str = Field(..., description="Detailed explanation of the novelty score")


# ---------------------------------------------------------------------------
# 6. Research & Market Gaps
# ---------------------------------------------------------------------------
class ResearchGapSchema(PipelineBaseSchema):
    unmet_needs: List[str] = Field(default_factory=list, description="Real user needs ignored by existing solutions")
    technical_white_spaces: List[str] = Field(default_factory=list, description="Unexplored technical architectures or methods")
    market_gaps: List[str] = Field(default_factory=list, description="Underserved market segments or workflows")
    recommended_angles: List[str] = Field(default_factory=list, description="High-leverage angles the project should pursue")


# ---------------------------------------------------------------------------
# 7. Mutation Engine
# ---------------------------------------------------------------------------
class MutationItemSchema(PipelineBaseSchema):
    id: str = Field(..., description="Unique slug or id e.g. 'edge_offline', 'hardware_constrained'")
    title: str = Field(..., description="Descriptive mutation title e.g. 'Edge-AI / Offline-First Mutation'")
    mutation_type: str = Field(..., description="Type: edge_offline, privacy_first, community_driven, agentic_workflow, low_cost_hardware")
    rationale: str = Field(..., description="Why this mutation transforms a generic idea into a winning project")
    key_modifications: List[str] = Field(default_factory=list, description="Specific features added or changed")
    impact_on_novelty: str = Field(..., description="How this mutation elevates the novelty and defensibility")
    selected: bool = Field(default=False, description="Whether the user selected this mutation")


class MutationEngineSchema(PipelineBaseSchema):
    mutations: List[MutationItemSchema] = Field(default_factory=list, description="Possible transformative project mutations")
    pivot_recommendation: str = Field(..., description="The single highest-impact mutation recommended by AI")


# ---------------------------------------------------------------------------
# 8. Reality Check / Feasibility
# ---------------------------------------------------------------------------
class RealityCheckSchema(PipelineBaseSchema):
    buildability_score: float = Field(..., description="Feasibility score from 0 to 100")
    feasibility_rating: str = Field(..., description="'High Feasibility', 'Moderate Feasibility', 'High Risk / Complex'")
    technical_prerequisites: List[str] = Field(default_factory=list, description="Skills, APIs, or tools needed to build")
    data_prerequisites: List[str] = Field(default_factory=list, description="Datasets or training data required")
    hardware_prerequisites: List[str] = Field(default_factory=list, description="Specific compute, sensors, or hardware needed")
    regulatory_or_ethical_risks: List[str] = Field(default_factory=list, description="Legal, GDPR, HIPAA, or safety considerations")
    mvp_complexity_weeks: int = Field(default=4, description="Realistic MVP development time in weeks for a small team")


# ---------------------------------------------------------------------------
# 9. Failure Simulation
# ---------------------------------------------------------------------------
class FailureScenarioSchema(PipelineBaseSchema):
    scenario_title: str = Field(..., description="Title of the failure mode e.g. 'Data Starvation at Scale'")
    trigger: str = Field(..., description="What event or dynamic triggers this failure")
    root_cause: str = Field(..., description="Underlying architectural or behavioral reason")
    probability: str = Field(..., description="'Low', 'Medium', or 'High'")
    impact: str = Field(..., description="'Moderate', 'Severe', or 'Fatal'")
    mitigation_strategy: str = Field(..., description="Concrete architectural or operational safeguard")


class FailureSimulationSchema(PipelineBaseSchema):
    failure_modes: List[FailureScenarioSchema] = Field(default_factory=list, description="Anticipated failure modes")
    kill_factor: str = Field(..., description="The single biggest vulnerability that could kill the project")


# ---------------------------------------------------------------------------
# 10. Impact & SDG Mapping
# ---------------------------------------------------------------------------
class SDGItemSchema(PipelineBaseSchema):
    sdg_number: int = Field(..., description="UN SDG number (1 to 17)")
    sdg_name: str = Field(..., description="Name of the SDG goal")
    target: str = Field(..., description="Specific target within the SDG")
    alignment_rationale: str = Field(..., description="How this specific project directly advances this target")


class ImpactAndSDGSchema(PipelineBaseSchema):
    sdg_alignments: List[SDGItemSchema] = Field(default_factory=list, description="Aligned UN SDGs")
    quantifiable_metrics: List[str] = Field(default_factory=list, description="Metrics to prove real-world impact")
    beneficiary_reach: str = Field(..., description="Who benefits and estimated scale of impact")
    environmental_or_social_impact: str = Field(..., description="Summary of positive externalities")


# ---------------------------------------------------------------------------
# 11. Technology Decision
# ---------------------------------------------------------------------------
class TechTradeOffSchema(PipelineBaseSchema):
    layer: str = Field(..., description="Layer e.g. Frontend, Backend, Database, AI/ML, Deployment")
    selected_tech: str = Field(..., description="Selected framework or technology")
    alternative_considered: str = Field(..., description="Alternative evaluated")
    reason_selected: str = Field(..., description="Why selected is superior for this specific project")
    reason_rejected: str = Field(..., description="Why the alternative was rejected")


class TechnologyDecisionSchema(PipelineBaseSchema):
    recommended_stack: Dict[str, str] = Field(default_factory=dict, description="Key-value mapping of stack components")
    trade_offs: List[TechTradeOffSchema] = Field(default_factory=list, description="Rigorous trade-off justifications")
    architecture_pattern: str = Field(..., description="Pattern e.g. Event-Driven Microservices, Modular Monolith, Edge-Compute")


# ---------------------------------------------------------------------------
# 12. Architecture & Mermaid
# ---------------------------------------------------------------------------
class ArchitectureComponentSchema(PipelineBaseSchema):
    name: str = Field(..., description="Component or subsystem name")
    role: str = Field(..., description="Responsibility in the system")
    technologies: str = Field(..., description="Specific tools / libraries used")
    dependencies: List[str] = Field(default_factory=list, description="Downstream or upstream dependencies")


class ArchitectureSchema(PipelineBaseSchema):
    mermaid_diagram: str = Field(..., description="Valid Mermaid.js graph TD or flowchart code")
    components: List[ArchitectureComponentSchema] = Field(default_factory=list, description="System components breakdown")
    data_flow_description: str = Field(default="", description="End-to-end data lifecycle from input to output")


# ---------------------------------------------------------------------------
# 13. Execution Roadmap
# ---------------------------------------------------------------------------
class RoadmapPhaseSchema(PipelineBaseSchema):
    phase_number: int = Field(..., description="Phase sequence number (1, 2, 3...)")
    phase_name: str = Field(..., description="Phase name e.g. 'Foundations & Data Pipeline'")
    duration_weeks: int = Field(..., description="Estimated weeks to execute")
    deliverables: List[str] = Field(default_factory=list, description="Concrete testable deliverables")
    key_risks: List[str] = Field(default_factory=list, description="Risks during this phase")


class RoadmapSchema(PipelineBaseSchema):
    phases: List[RoadmapPhaseSchema] = Field(default_factory=list, description="Structured project phases")
    mvp_milestone: str = Field(default="", description="The defining MVP completion criteria")
    critical_path_items: List[str] = Field(default_factory=list, description="Items on the critical path")


# ---------------------------------------------------------------------------
# 14. Judge Attack Simulation
# ---------------------------------------------------------------------------
class JudgeQuestionSchema(PipelineBaseSchema):
    id: str = Field(..., description="Question identifier e.g. 'Q1'")
    category: str = Field(..., description="Category: Technical, Defensibility, Business Model, or Ethical")
    question: str = Field(..., description="Tough, critical question likely asked by hackathon judge or VC")
    why_judges_ask: str = Field(default="", description="The underlying skepticism behind the question")
    model_defense_strategy: str = Field(default="", description="Winning answer strategy and evidence to cite")
    suggested_talking_points: List[str] = Field(default_factory=list, description="Bullet points to include in live pitch response")


class JudgeAttackSchema(PipelineBaseSchema):
    questions: List[JudgeQuestionSchema] = Field(default_factory=list, description="Set of rigorous judge attack questions")
    overall_pitch_defense_tip: str = Field(default="", description="Key piece of advice for presenting this idea convincingly")


# ---------------------------------------------------------------------------
# 15. Master Project Blueprint
# ---------------------------------------------------------------------------
class MasterBlueprintSchema(PipelineBaseSchema):
    executive_summary: str = Field(default="", description="High-level project summary synthesized across all modules")
    verified_problem_statement: str = Field(default="", description="Grounded problem definition supported by evidence")
    target_audience: List[str] = Field(default_factory=list, description="Validated beneficiaries")
    core_innovation_and_gap: str = Field(default="", description="The exact white space this project claims")
    selected_mutation: Optional[str] = Field(None, description="The chosen mutation / architectural pivot if any")
    system_architecture_summary: str = Field(default="", description="High-level architecture summary")
    execution_strategy: str = Field(default="", description="Strategy for delivering the MVP")
    elevator_pitch: str = Field(default="", description="30-second compelling elevator pitch")
    judge_defense_summary: str = Field(default="", description="Key counter-arguments prepared for critics")


__all__ = [
    "PipelineBaseSchema",
    "IdeaUnderstandingSchema",
    "ExistingSolutionSchema",
    "SolutionLandscapeSchema",
    "ClaimEvidenceSchema",
    "EvidenceBoardSchema",
    "FeatureOverlapSchema",
    "SimilarityAnalysisSchema",
    "NoveltyScoreSchema",
    "ResearchGapSchema",
    "MutationItemSchema",
    "MutationEngineSchema",
    "RealityCheckSchema",
    "FailureScenarioSchema",
    "FailureSimulationSchema",
    "SDGItemSchema",
    "ImpactAndSDGSchema",
    "TechTradeOffSchema",
    "TechnologyDecisionSchema",
    "ArchitectureComponentSchema",
    "ArchitectureSchema",
    "RoadmapPhaseSchema",
    "RoadmapSchema",
    "JudgeQuestionSchema",
    "JudgeAttackSchema",
    "MasterBlueprintSchema",
]
