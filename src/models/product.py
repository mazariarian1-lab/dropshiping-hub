"""Product research data model."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductCandidate:
    name: str
    customer_problem: str = ""
    demand_evidence: str = ""
    trend_12m: str = ""
    trend_5y: str = ""
    seasonality: str = ""
    supplier: str = ""
    us_warehouse: Optional[bool] = None
    delivery_days: Optional[str] = None
    product_cost: Optional[float] = None
    shipping_cost: Optional[float] = None
    retail_price: Optional[float] = None
    competition: str = ""
    ad_potential: str = ""
    risk: str = ""
    source_url: str = ""
    verification_status: str = "NEEDS LIVE VERIFICATION"
    evidence: list[str] = field(default_factory=list)

    @property
    def landed_cost(self) -> Optional[float]:
        if self.product_cost is None or self.shipping_cost is None:
            return None
        return round(self.product_cost + self.shipping_cost, 2)

    @property
    def gross_profit(self) -> Optional[float]:
        landed = self.landed_cost
        if landed is None or self.retail_price is None:
            return None
        return round(self.retail_price - landed, 2)

    @property
    def gross_margin_percent(self) -> Optional[float]:
        if self.gross_profit is None or not self.retail_price:
            return None
        return round((self.gross_profit / self.retail_price) * 100, 2)
