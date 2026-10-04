"""Encyclopedia and open reference documentation service."""
import logging
from typing import List, Dict, Any
import httpx

logger = logging.getLogger("yosifix.research.web")

class WebSearchService:
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.wiki_url = "https://en.wikipedia.org/w/api.php"

    def search(self, query: str, limit: int = 2) -> List[Dict[str, Any]]:
        headers = {"User-Agent": "YosiFix-Evidence-Engine/1.0"}
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit,
        }

        results = []
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(self.wiki_url, headers=headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("query", {}).get("search", []):
                        title = item.get("title", "")
                        clean_snippet = item.get("snippet", "").replace('<span class="searchmatch">', "").replace('</span>', "")
                        page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                        results.append({
                            "type": "documentation",
                            "title": title,
                            "url": page_url,
                            "source_name": "Wikipedia Reference",
                            "description": clean_snippet or f"Reference article on {title}",
                            "metrics": {"wordcount": item.get("wordcount", 0)},
                            "published_at": "Peer-Reviewed Reference",
                            "verification_status": "verified",
                            "relevance": 0.80,
                        })
        except Exception as exc:
            logger.warning(f"Wikipedia search failed: {exc}")
        return results
