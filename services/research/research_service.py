"""Unified multi-channel research orchestrator."""
import logging
from typing import Dict, List, Any
from services.research.github_service import GitHubResearchService
from services.research.paper_service import PaperResearchService
from services.research.dataset_service import DatasetResearchService
from services.research.product_service import ProductResearchService
from services.research.web_search_service import WebSearchService
from services.research.query_generator import generate_research_queries
from services.research.evidence_service import EvidenceService

logger = logging.getLogger("yosifix.research.orchestrator")

class ResearchService:
    def __init__(self):
        self.github = GitHubResearchService()
        self.papers = PaperResearchService()
        self.datasets = DatasetResearchService()
        self.products = ProductResearchService()
        self.web = WebSearchService()
        self.evidence_mgr = EvidenceService()

    def conduct_research(self, context: Dict[str, Any], idea_id: int = None) -> List[Dict[str, Any]]:
        """Run multi-channel research across code, papers, datasets, products and docs."""
        queries = generate_research_queries(context)
        domain = context.get("domain", "Technology")
        all_findings = []

        # 1. GitHub Repositories
        for q in queries.get("github", [])[:1]:
            repos = self.github.search(q, limit=3)
            all_findings.extend(repos)

        # 2. Papers / Literature
        for q in queries.get("papers", [])[:1]:
            papers = self.papers.search(q, limit=2)
            all_findings.extend(papers)

        # 3. Datasets
        for q in queries.get("datasets", [])[:1]:
            datasets = self.datasets.search(q, limit=2)
            all_findings.extend(datasets)

        # 4. Products / Existing tools
        for q in queries.get("products", [])[:1]:
            products = self.products.search(q, domain=domain, limit=3)
            all_findings.extend(products)

        # 5. Open encyclopedia / documentation
        for q in queries.get("web", [])[:1]:
            docs = self.web.search(q, limit=2)
            all_findings.extend(docs)

        # Fallback guarantee: if network calls produced fewer than 3 items, supply baseline domain items
        if len(all_findings) < 2:
            products = self.products.search(domain, domain=domain, limit=3)
            all_findings.extend(products)

        # Sync to database if idea_id provided
        if idea_id:
            return self.evidence_mgr.sync_evidence_to_db(idea_id, all_findings)

        from services.research.deduplicator import deduplicate_evidence_items
        from services.research.evidence_normalizer import normalize_evidence_records
        return normalize_evidence_records(deduplicate_evidence_items(all_findings))
