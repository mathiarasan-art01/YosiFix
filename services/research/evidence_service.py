"""Evidence management service: normalizes, codes, and syncs verified evidence to DB."""
from typing import List, Dict, Any
from extensions import db
from models.evidence import EvidenceSource
from services.research.evidence_normalizer import normalize_evidence_records
from services.research.deduplicator import deduplicate_evidence_items

class EvidenceService:
    def sync_evidence_to_db(self, idea_id: int, raw_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate, normalize into EV-### codes, and save to EvidenceSource table."""
        deduped = deduplicate_evidence_items(raw_findings)
        normalized = normalize_evidence_records(deduped, start_index=1)

        # Clear existing evidence for this project and re-populate
        try:
            EvidenceSource.query.filter_by(idea_id=idea_id).delete()
            for item in normalized:
                source = EvidenceSource(
                    idea_id=idea_id,
                    code=item["code"],
                    type=item["type"],
                    title=item["title"][:300],
                    url=item["url"][:600],
                    source_name=item["source_name"][:60],
                    description=item["description"],
                    published_at=item["published_at"][:30],
                    metrics=item["metrics"],
                    relevance=item["relevance"],
                    verification_status=item["verification_status"],
                )
                db.session.add(source)
            db.session.commit()
        except Exception:
            db.session.rollback()

        return normalized
