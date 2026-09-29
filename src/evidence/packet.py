"""Structured evidence packets for specialist research outputs."""

from dataclasses import dataclass, field
from typing import Optional


VALID_STATES = {
    "VERIFIED",
    "PARTIALLY VERIFIED",
    "ESTIMATE",
    "RESEARCH CANDIDATE",
    "NEEDS LIVE VERIFICATION",
    "REJECTED",
}


@dataclass
class EvidenceClaim:
    claim: str
    value: str
    source: str = ""
    source_type: str = ""
    observed_at: str = ""
    confidence: Optional[str] = None
    verification_state: str = "NEEDS LIVE VERIFICATION"
    notes: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.claim.strip(): errors.append("evidence claim is missing")
        if not self.value.strip(): errors.append("evidence value is missing")
        if self.verification_state not in VALID_STATES:
            errors.append("invalid evidence verification state")
        if self.verification_state == "VERIFIED" and not self.source.strip():
            errors.append("verified evidence requires a source")
        return errors


@dataclass
class EvidencePacket:
    request_id: str
    role: str
    status: str = "PARTIAL"
    candidates: list[dict] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)
    evidence: list[EvidenceClaim] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    recommended_next_checks: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors = []
        if not self.request_id.strip(): errors.append("request_id is required")
        if not self.role.strip(): errors.append("role is required")
        if self.status not in {"COMPLETE", "PARTIAL", "BLOCKED", "NO_VALID_FINDINGS"}:
            errors.append("invalid packet status")
        for claim in self.evidence:
            errors.extend(claim.validate())
        if self.conflicts:
            errors.append("critical evidence conflicts require resolution")
        return errors
