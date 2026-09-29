"""Research request normalization and validation."""

from dataclasses import dataclass, field
from typing import List

@dataclass
class ResearchRequest:
    market: str = "USA"
    currency: str = "USD"
    research_depth: str = "deep"
    max_final_candidates: int = 5
    allow_fewer_than_max: bool = True
    allow_zero_results: bool = True
    product_types: List[str] = field(default_factory=lambda: ["evergreen", "seasonal"])
    retail_price_max: float = 50.0
    fulfillment_min_days: int = 4
    fulfillment_max_days: int = 12
    preferred_supplier: str = "CJ Dropshipping"
    preferred_warehouse: str = "US"
    consumer_problem_required: bool = True
    trend_windows: List[str] = field(default_factory=lambda: ["12M", "5Y"])
    ad_potential_required: bool = True
    evidence_first: bool = True

    def validate(self) -> List[str]:
        errors = []
        if self.market != "USA":
            errors.append("market must be USA")
        if self.currency != "USD":
            errors.append("currency must be USD")
        if self.research_depth not in {"standard", "deep"}:
            errors.append("research_depth must be standard or deep")
        if self.max_final_candidates < 1:
            errors.append("max_final_candidates must be >= 1")
        if self.retail_price_max <= 0:
            errors.append("retail_price_max must be > 0")
        if self.fulfillment_min_days < 0 or self.fulfillment_max_days < self.fulfillment_min_days:
            errors.append("invalid fulfillment day range")
        if not self.allow_fewer_than_max:
            errors.append("allow_fewer_than_max must remain true")
        if not self.allow_zero_results:
            errors.append("allow_zero_results must remain true")
        if self.preferred_warehouse.upper() != "US":
            errors.append("preferred_warehouse must remain US")
        if not self.evidence_first:
            errors.append("evidence_first must remain true")
        return errors
