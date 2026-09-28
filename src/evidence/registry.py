"""Evidence registry for source-backed research claims."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class EvidenceItem:
    claim: str
    source_url: str
    source_type: str
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "UNVERIFIED"
    notes: str = ""

    def verify(self, notes: str = "") -> None:
        self.status = "VERIFIED"
        self.notes = notes


class EvidenceRegistry:
    def __init__(self) -> None:
        self.items: list[EvidenceItem] = []

    def add(self, item: EvidenceItem) -> None:
        self.items.append(item)

    def verified(self) -> list[EvidenceItem]:
        return [item for item in self.items if item.status == "VERIFIED"]

    def has_verified_source_for(self, keyword: str) -> bool:
        keyword = keyword.lower()
        return any(keyword in item.claim.lower() and item.status == "VERIFIED" for item in self.items)
