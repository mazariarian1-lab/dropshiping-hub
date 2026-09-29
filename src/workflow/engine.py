"""Evidence-first research workflow state machine."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from .research_request import ResearchRequest

class Stage(str, Enum):
    NORMALIZE = "normalize_request"
    DISCOVERY = "opportunity_discovery"
    NEED = "consumer_need_validation"
    TREND = "trend_validation"
    SUPPLIER = "supplier_fulfillment_validation"
    ECONOMICS = "economics"
    COMPETITION = "competition"
    ADS = "ad_validation"
    RISK = "risk_policy_review"
    EVIDENCE_GATE = "evidence_gate"
    FINAL = "final_shortlist"

@dataclass
class WorkflowState:
    request: ResearchRequest
    stage: Stage = Stage.NORMALIZE
    candidates: List[Dict] = field(default_factory=list)
    findings: List[Dict] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)

class ResearchWorkflow:
    """Orchestrates stages; it does not fabricate missing evidence."""

    def __init__(self, request: ResearchRequest):
        self.state = WorkflowState(request=request)

    def run_stage(self, stage: Stage, findings: List[Dict] | None = None) -> WorkflowState:
        self.state.stage = stage
        if findings:
            self.state.findings.extend(findings)
        return self.state

    def final_candidates(self) -> List[Dict]:
        eligible = []
        for candidate in self.state.candidates:
            if candidate.get("status") == "VERIFIED" and not candidate.get("blockers"):
                eligible.append(candidate)
        return eligible[: self.state.request.max_final_candidates]

    def summary(self) -> Dict:
        final = self.final_candidates()
        return {
            "stage": self.state.stage.value,
            "candidate_count": len(self.state.candidates),
            "final_count": len(final),
            "message": (
                "NO PRODUCT PASSED THE CURRENT EVIDENCE GATES."
                if not final else
                "Final candidates are ready for human review."
            ),
            "blockers": self.state.blockers,
        }
