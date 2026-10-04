"""Normalizes raw multi-source search results into canonical EV-### evidence items."""
from typing import List, Dict, Any
from services.common.security import safe_external_url

def normalize_evidence_records(raw_items: List[Dict[str, Any]], start_index: int = 1) -> List[Dict[str, Any]]:
    """Format diverse API results into structured evidence schema with EV-### codes."""
    normalized = []
    idx = start_index

    for raw in raw_items:
        code = f"EV-{idx:03d}"
        url = safe_external_url(raw.get("url", ""))
        title = (raw.get("title") or "Unnamed Source").strip()
        desc = (raw.get("description") or "").strip()
        src_name = raw.get("source_name") or "External Registry"
        ev_type = raw.get("type", "documentation")
        
        normalized.append({
            "id": code,
            "code": code,
            "type": ev_type,
            "title": title,
            "url": url,
            "source_name": src_name,
            "description": desc,
            "published_at": raw.get("published_at", ""),
            "metrics": raw.get("metrics", {}),
            "relevance": float(raw.get("relevance", 0.85)),
            "verification_status": raw.get("verification_status", "verified"),
        })
        idx += 1

    return normalized
