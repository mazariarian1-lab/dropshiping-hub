"""Normalized discovery candidates and deterministic deduplication."""

from dataclasses import dataclass, field
import re
from typing import Iterable


def _key(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()
    return re.sub(r"\s+", " ", value)


@dataclass
class CandidateRecord:
    name: str
    source: str = ""
    source_url: str = ""
    customer_problem: str = ""
    product_type: str = ""
    evidence: list[dict] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    status: str = "RESEARCH CANDIDATE"

    @property
    def dedupe_key(self) -> str:
        return _key(self.name)


def deduplicate_candidates(candidates: Iterable[CandidateRecord]) -> list[CandidateRecord]:
    """Keep the first normalized product name; merge evidence/URLs from duplicates."""
    unique: dict[str, CandidateRecord] = {}
    for candidate in candidates:
        key = candidate.dedupe_key
        if not key:
            continue
        if key not in unique:
            unique[key] = candidate
            continue
        existing = unique[key]
        existing.evidence.extend(item for item in candidate.evidence if item not in existing.evidence)
        if not existing.source_url and candidate.source_url:
            existing.source_url = candidate.source_url
        if not existing.customer_problem and candidate.customer_problem:
            existing.customer_problem = candidate.customer_problem
        existing.blockers.extend(item for item in candidate.blockers if item not in existing.blockers)
    return list(unique.values())
