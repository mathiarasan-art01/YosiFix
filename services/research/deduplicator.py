"""Deduplication utilities for research items."""
from typing import List, Dict, Any
from urllib.parse import urlparse

def deduplicate_evidence_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate external findings by normalized title and URL."""
    seen_urls = set()
    seen_titles = set()
    unique_items = []

    for item in items:
        url = (item.get("url") or "").strip().rstrip("/")
        title = (item.get("title") or "").strip().lower()

        # Simplify url
        norm_url = ""
        if url:
            parsed = urlparse(url)
            norm_url = f"{parsed.netloc}{parsed.path}".lower().rstrip("/")

        if norm_url and norm_url in seen_urls:
            continue
        if title and title in seen_titles:
            continue

        if norm_url:
            seen_urls.add(norm_url)
        if title:
            seen_titles.add(title)

        unique_items.append(item)

    return unique_items
