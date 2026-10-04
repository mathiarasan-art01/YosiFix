"""Content-addressed caching service for analysis pipeline stages."""
import hashlib
import json
import logging
from typing import Dict, Any, Optional
from extensions import db
from models.analysis import AnalysisCache

logger = logging.getLogger("yosifix.analysis.cache")


class AnalysisCacheService:
    """Manages content-addressed caching to prevent duplicate Groq inference."""

    @staticmethod
    def compute_cache_key(stage_key: str, payload: Dict[str, Any]) -> str:
        """Deterministically hash the stage key and normalized JSON payload."""
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(f"{stage_key}:{serialized}".encode("utf-8")).hexdigest()

    @staticmethod
    def get(stage_key: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve cached output if present, updating hit counter."""
        cache_key = AnalysisCacheService.compute_cache_key(stage_key, payload)
        try:
            entry = AnalysisCache.query.filter_by(cache_key=cache_key).first()
            if entry:
                entry.hits += 1
                db.session.commit()
                logger.info(f"Cache HIT for stage '{stage_key}' (hits: {entry.hits})")
                return entry.output
        except Exception as e:
            logger.debug(f"Cache lookup failed or not in active session: {e}")
        return None

    @staticmethod
    def set(stage_key: str, payload: Dict[str, Any], output: Dict[str, Any], engine: str = "") -> None:
        """Store stage output in cache."""
        cache_key = AnalysisCacheService.compute_cache_key(stage_key, payload)
        try:
            entry = AnalysisCache.query.filter_by(cache_key=cache_key).first()
            if not entry:
                entry = AnalysisCache(
                    cache_key=cache_key,
                    stage_key=stage_key,
                    output=output,
                    engine=engine,
                    hits=0,
                )
                db.session.add(entry)
            else:
                entry.output = output
                entry.engine = engine
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.debug(f"Failed to persist cache entry for stage '{stage_key}': {e}")
