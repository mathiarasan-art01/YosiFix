"""GitHub repository research service."""
import os
import logging
from typing import List, Dict, Any
import httpx

logger = logging.getLogger("yosifix.research.github")

class GitHubResearchService:
    def __init__(self, token: str = None, timeout: float = 6.0):
        self.token = token or os.getenv("GITHUB_TOKEN", "").strip()
        self.timeout = timeout
        self.base_url = "https://api.github.com/search/repositories"

    def search(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "YosiFix-Evidence-Engine/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": limit,
        }

        results = []
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(self.base_url, headers=headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("items", []):
                        results.append({
                            "type": "github",
                            "title": item.get("full_name", ""),
                            "url": item.get("html_url", ""),
                            "source_name": "GitHub",
                            "description": item.get("description") or f"Open-source repository for {query}",
                            "metrics": {
                                "stars": item.get("stargazers_count", 0),
                                "forks": item.get("forks_count", 0),
                                "language": item.get("language") or "Code",
                            },
                            "published_at": item.get("created_at", "")[:10],
                            "verification_status": "verified",
                            "relevance": 0.92,
                        })
        except Exception as exc:
            logger.warning(f"GitHub search failed for query '{query}': {exc}")
        return results
