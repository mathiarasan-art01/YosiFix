"""Invalidation Manager: selectively invalidates downstream stages when inputs change."""
import logging
from typing import List, Optional
from services.analysis.dependency_graph import DependencyGraph
from services.analysis.context import AnalysisContext

logger = logging.getLogger("yosifix.analysis.invalidation")


class InvalidationManager:
    """Coordinates selective stage invalidation and cache eviction."""

    @staticmethod
    def invalidate_downstream(context: AnalysisContext, changed_stage: str) -> List[str]:
        """Invalidate stages downstream of changed_stage, removing them from completed_stages."""
        affected = DependencyGraph.get_downstream_stages(changed_stage)
        if not affected:
            return []

        logger.info(f"Invalidating downstream stages for '{changed_stage}': {affected}")

        for stage in affected:
            if stage in context.completed_stages:
                context.completed_stages.remove(stage)

        context.current_stage = changed_stage
        return affected

    @staticmethod
    def invalidate_for_mutation_selection(context: AnalysisContext) -> List[str]:
        """Invalidate all stages dependent on strategic mutation choice."""
        return InvalidationManager.invalidate_downstream(context, "mutation_engine")
