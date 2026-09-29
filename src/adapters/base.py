"""Contracts shared by all external research adapters."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

PACKET_STATUSES = {"COMPLETE", "PARTIAL", "BLOCKED", "NO_VALID_FINDINGS"}

@dataclass(frozen=True)
class AdapterCapabilities:
    name: str
    role: str
    source_type: str
    capabilities: tuple[str, ...] = ()
    live_connected: bool = False

@dataclass
class AdapterResult:
    adapter: str
    status: str
    request_id: str
    generated_at: str
    candidates: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    recommended_next_checks: List[str] = field(default_factory=list)

    @classmethod
    def not_connected(cls, adapter: str, request_id: str, reason: str) -> "AdapterResult":
        return cls(adapter=adapter, status="BLOCKED", request_id=request_id,
                   generated_at=datetime.now(timezone.utc).isoformat(),
                   unknowns=[reason],
                   recommended_next_checks=[f"Connect and authorize the {adapter} adapter before using live evidence."])

    def to_packet(self) -> Dict[str, Any]:
        return {"request_id": self.request_id, "role": self.adapter, "status": self.status,
                "candidates": self.candidates, "findings": self.findings, "evidence": self.evidence,
                "unknowns": self.unknowns, "conflicts": self.conflicts,
                "recommended_next_checks": self.recommended_next_checks}

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.adapter.strip(): errors.append("adapter is required")
        if not self.request_id.strip(): errors.append("request_id is required")
        if self.status not in PACKET_STATUSES: errors.append("invalid adapter result status")
        if not self.generated_at.strip(): errors.append("generated_at is required")
        if self.status == "COMPLETE" and not (self.candidates or self.findings or self.evidence):
            errors.append("COMPLETE result must contain findings or evidence")
        return errors

class ResearchAdapter(ABC):
    """Minimal interface; implementations must never invent unavailable evidence."""
    capabilities: AdapterCapabilities

    @abstractmethod
    def research(self, request: Dict[str, Any], request_id: str) -> AdapterResult:
        raise NotImplementedError
