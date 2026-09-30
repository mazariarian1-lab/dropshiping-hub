"""Evidence-first research workflow state machine."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from .research_request import ResearchRequest
from .gates import evaluate_candidate
from src.pipeline import merge_packets

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

    def ingest_packets(self, packets: List[Dict]) -> WorkflowState:
        """Merge specialist outputs before deterministic decision gates."""
        self.state.candidates = merge_packets(packets)
        self.state.stage = Stage.EVIDENCE_GATE
        return self.state

    @staticmethod
    def _score(candidate: Dict) -> float:
        margin = float(candidate.get("calculated_gross_margin_percent", 0))
        score = min(max((margin - 40.0) / 60.0, 0.0), 1.0) * 25.0
        score += {"GROWING": 15.0, "STABLE": 8.0, "DECLINING": 0.0}.get(str(candidate.get("trend_growth_signal", "")).upper(), 0.0)
        score += {"GROWING": 10.0, "STABLE": 5.0, "DECLINING": 0.0}.get(str(candidate.get("trend_long_term_signal", "")).upper(), 0.0)
        delivery = candidate.get("delivery_days")
        if isinstance(delivery, (tuple, list)) and len(delivery) == 2:
            midpoint = (float(delivery[0]) + float(delivery[1])) / 2.0
            score += max(0.0, min(10.0, (12.0 - midpoint) / 8.0 * 10.0))
        if candidate.get("seasonality_signal") is True: score += 5.0
        score += {"LOW": 10.0, "MEDIUM": 5.0, "HIGH": 0.0}.get(str(candidate.get("competition", "")).upper(), 0.0)
        score += {"HIGH": 10.0, "MEDIUM": 6.0, "LOW": 2.0}.get(str(candidate.get("ad_potential", "")).upper(), 0.0)
        score += {"LOW": 10.0, "MEDIUM": 5.0, "HIGH": 0.0}.get(str(candidate.get("risk_level", "")).upper(), 0.0)
        if candidate.get("customer_problem"): score += 5.0
        return round(min(score, 100.0), 2)

    @staticmethod
    def _score_breakdown(candidate: Dict) -> Dict:
        return {
            "margin": candidate.get("calculated_gross_margin_percent"),
            "trend_12m": candidate.get("trend_growth_signal"),
            "trend_5y": candidate.get("trend_long_term_signal"),
            "delivery_days": candidate.get("delivery_days"),
            "seasonality": candidate.get("seasonality_signal"),
            "competition": candidate.get("competition"),
            "ad_potential": candidate.get("ad_potential"),
            "risk": candidate.get("risk_level"),
            "consumer_problem": bool(candidate.get("customer_problem")),
        }
    def final_candidates(self) -> List[Dict]:
        eligible = []
        for candidate in self.state.candidates:
            blockers = evaluate_candidate(
                candidate,
                fulfillment_min=self.state.request.fulfillment_min_days,
                fulfillment_max=self.state.request.fulfillment_max_days,
                retail_price_max=self.state.request.retail_price_max,
            )
            candidate["blockers"] = blockers
            if not blockers:
                candidate["product_score"] = self._score(candidate)
                candidate["score_breakdown"] = self._score_breakdown(candidate)
                eligible.append(candidate)
        eligible.sort(key=lambda item: item.get("product_score", 0), reverse=True)
        self.state.stage = Stage.FINAL if eligible else Stage.EVIDENCE_GATE
        return eligible[: self.state.request.max_final_candidates]

    def summary(self) -> Dict:
        final = self.final_candidates()
        return {
            "stage": self.state.stage.value,
            "candidate_count": len(self.state.candidates),
            "final_count": len(final),
            "verified_count": sum(1 for c in self.state.candidates if c.get("status") == "VERIFIED"),
            "rejected_count": sum(1 for c in self.state.candidates if c.get("blockers")),
            "top_scores": [{"name": c.get("name"), "score": c.get("product_score")} for c in final],
            "message": (
                "NO PRODUCT PASSED THE CURRENT EVIDENCE GATES."
                if not final else
                "Final candidates are ready for human review."
            ),
            "blockers": self.state.blockers,
        }
