"""Deterministic readiness gates for final product approval."""

from typing import Iterable

CRITICAL_FIELDS = (
    "supplier", "us_warehouse", "delivery_days", "product_cost",
    "shipping_cost", "retail_price", "trend_12m", "trend_5y", "source_url",
)


def evaluate_candidate(
    candidate: dict,
    fulfillment_min: int = 4,
    fulfillment_max: int = 12,
    retail_price_max: float = 50.0,
) -> list[str]:
    blockers: list[str] = []
    if candidate.get("status") != "VERIFIED":
        blockers.append("critical evidence is not VERIFIED")
    if candidate.get("conflicts"):
        blockers.append("critical evidence conflict exists")
    for field in CRITICAL_FIELDS:
        value = candidate.get(field)
        if value in (None, "", "UNKNOWN", "NEEDS LIVE VERIFICATION"):
            blockers.append(f"missing critical evidence: {field}")
    if candidate.get("us_warehouse") is not True:
        blockers.append("US warehouse is not verified")
    price = candidate.get("retail_price")
    if price is not None and price > retail_price_max:
        blockers.append(f"retail price exceeds ${retail_price_max:g}")
    margin = candidate.get("gross_margin_percent")
    if margin is not None and margin < 40:
        blockers.append("gross margin is below 40%")
    delivery = candidate.get("delivery_days")
    if isinstance(delivery, (tuple, list)) and len(delivery) == 2:
        if delivery[0] < fulfillment_min or delivery[1] > fulfillment_max:
            blockers.append(f"delivery is outside {fulfillment_min}-{fulfillment_max} day target")
    elif delivery and isinstance(delivery, str):
        normalized = delivery.replace("–", "-").replace("—", "-")
        expected = f"{fulfillment_min}-{fulfillment_max}"
        if expected not in normalized:
            blockers.append(f"delivery does not explicitly match {fulfillment_min}-{fulfillment_max} day target")
    return list(dict.fromkeys(blockers))


def ready_candidates(candidates: Iterable[dict], limit: int = 5) -> list[dict]:
    ready = []
    for candidate in candidates:
        blockers = evaluate_candidate(candidate)
        candidate["blockers"] = blockers
        if not blockers:
            ready.append(candidate)
    return ready[:limit]
