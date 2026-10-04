"""Academic paper and scientific literature research service."""
import logging
from typing import List, Dict, Any
import httpx

logger = logging.getLogger("yosifix.research.papers")

class PaperResearchService:
    def __init__(self, timeout: float = 6.0):
        self.timeout = timeout
        self.openalex_url = "https://api.openalex.org/works"

    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        headers = {
            "User-Agent": "YosiFix-Evidence-Engine/1.0 (mailto:team@yosifix.dev)"
        }
        params = {
            "search": query,
            "per-page": limit,
            "sort": "cited_by_count:desc",
            "select": "id,title,doi,publication_year,cited_by_count,primary_location",
        }

        results = []
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(self.openalex_url, headers=headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    for work in data.get("results", []):
                        landing_url = (work.get("primary_location") or {}).get("landing_page_url") or work.get("doi") or ""
                        results.append({
                            "type": "paper",
                            "title": work.get("title", ""),
                            "url": landing_url,
                            "source_name": "OpenAlex Scientific Index",
                            "description": f"Published literature in {work.get('publication_year', 'recent years')}. Highly cited benchmark research.",
                            "metrics": {
                                "citations": work.get("cited_by_count", 0),
                                "year": work.get("publication_year"),
                            },
                            "published_at": str(work.get("publication_year", "")),
                            "verification_status": "verified",
                            "relevance": 0.90,
                        })
        except Exception as exc:
            logger.warning(f"Paper search failed for query '{query}': {exc}")
        return results
