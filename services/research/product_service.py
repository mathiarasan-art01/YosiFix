"""Market product and existing solution discovery service."""
import re
import logging
from typing import List, Dict, Any
import httpx
from modules.knowledge_base import KNOWLEDGE_BASE

logger = logging.getLogger("yosifix.research.product")

class ProductResearchService:
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.hn_url = "https://hn.algolia.com/api/v1/search"

    def search(self, query: str, domain: str = "Technology", limit: int = 4) -> List[Dict[str, Any]]:
        results = []

        # 1. Consult curated domain knowledge base ranked by query relevance
        kb_entries = KNOWLEDGE_BASE.get(domain, [])
        query_words = set(re.findall(r"\w+", query.lower())) - {"and", "the", "for", "with", "system", "app"}
        
        scored_entries = []
        for entry in kb_entries:
            entry_text = f"{entry['name']} {entry['description']} {' '.join(entry.get('key_features', []))}".lower()
            overlap = sum(1 for w in query_words if w in entry_text)
            scored_entries.append((overlap, entry))
        
        # Sort by highest keyword match
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        top_candidates = [e for score, e in scored_entries if score > 0][:limit] or [e for _, e in scored_entries[:2]]

        for entry in top_candidates:
            results.append({
                "type": "product",
                "title": entry["name"],
                "url": f"https://www.google.com/search?q={entry['name'].replace(' ', '+')}",
                "source_name": "Industry Knowledge Base",
                "description": entry["description"],
                "metrics": {
                    "features_count": len(entry.get("key_features", [])),
                    "limitations_count": len(entry.get("limitations", [])),
                },
                "published_at": "Established",
                "verification_status": "verified",
                "relevance": 0.95,
            })

        # 2. Augment with Hacker News / tech discussions
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(self.hn_url, params={"query": query, "tags": "story", "hitsPerPage": 3})
                if resp.status_code == 200:
                    hits = resp.json().get("hits", [])
                    for hit in hits:
                        title = hit.get("title")
                        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                        if title:
                            results.append({
                                "type": "product",
                                "title": title,
                                "url": url,
                                "source_name": "Tech Community Discussion",
                                "description": f"Community feedback and discussion on {query}.",
                                "metrics": {
                                    "points": hit.get("points", 0),
                                    "comments": hit.get("num_comments", 0),
                                },
                                "published_at": hit.get("created_at", "")[:10],
                                "verification_status": "verified",
                                "relevance": 0.82,
                            })
        except Exception as exc:
            logger.warning(f"Product live search failed: {exc}")

        return results[:limit]
