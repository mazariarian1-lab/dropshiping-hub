"""Deterministic readiness gates for final product approval."""

from typing import Iterable

CRITICAL_FIELDS = (
    "supplier", "us_warehouse", "delivery_days", "product_cost",
    "shipping_cost", "retail_price", "trend_12m", "trend_5y", "source_url",
)


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def evaluate_candidate(candidate: dict, fulfillment_min: int = 4, fulfillment_max: int = 12, retail_price_max: float = 50.0) -> list[str]:
    blockers: list[str] = []
    if candidate.get("status") != "VERIFIED": blockers.append("critical evidence is not VERIFIED")
    if candidate.get("conflicts"): blockers.append("critical evidence conflict exists")
    for field in CRITICAL_FIELDS:
        value = candidate.get(field)
        if value in (None, "", "UNKNOWN", "NEEDS LIVE VERIFICATION"): blockers.append(f"missing critical evidence: {field}")
    if candidate.get("us_warehouse") is not True: blockers.append("US warehouse is not verified")
    if candidate.get("customer_problem") in (None, "", "UNKNOWN", "NEEDS LIVE VERIFICATION"): blockers.append("consumer problem evidence is missing")
    if candidate.get("ad_potential") in (None, "", "UNKNOWN", "NEEDS LIVE VERIFICATION"): blockers.append("ad potential evidence is missing")
    if candidate.get("risk_level") in (None, "", "UNKNOWN", "NEEDS LIVE VERIFICATION"): blockers.append("risk level evidence is missing")
    shipping_evidence = candidate.get("shipping_evidence")
    if not isinstance(shipping_evidence, dict) or shipping_evidence.get("destination") != "US": blockers.append("USA shipping evidence is not verified")
    price = candidate.get("retail_price")
    if not _number(price): blockers.append("retail price must be numeric")
    elif price > retail_price_max: blockers.append(f"retail price exceeds ${retail_price_max:g}")
    product_cost, shipping_cost = candidate.get("product_cost"), candidate.get("shipping_cost")
    if not _number(product_cost): blockers.append("product cost must be numeric")
    if not _number(shipping_cost): blockers.append("shipping cost must be numeric")
    if _number(product_cost) and _number(shipping_cost) and _number(price) and price > 0:
        landed = product_cost + shipping_cost
        margin = ((price - landed) / price) * 100
        candidate["landed_cost"] = round(landed, 2)
        candidate["calculated_gross_margin_percent"] = round(margin, 2)
        if margin < 40: blockers.append("calculated gross margin is below 40%")
        supplied = candidate.get("gross_margin_percent")
        if _number(supplied) and abs(supplied - margin) > 1.0: blockers.append("supplied gross margin conflicts with calculated margin")
    delivery = candidate.get("delivery_days")
    if isinstance(delivery, (tuple, list)) and len(delivery) == 2:
        if delivery[0] < fulfillment_min or delivery[1] > fulfillment_max: blockers.append(f"delivery is outside {fulfillment_min}-{fulfillment_max} day target")
    elif isinstance(delivery, str):
        normalized = delivery.replace("–", "-").replace("—", "-")
        if f"{fulfillment_min}-{fulfillment_max}" not in normalized: blockers.append(f"delivery does not explicitly match {fulfillment_min}-{fulfillment_max} day target")
    else: blockers.append(f"delivery must be evidenced within {fulfillment_min}-{fulfillment_max} days")
    return list(dict.fromkeys(blockers))


def ready_candidates(candidates, limit=5, fulfillment_min=4, fulfillment_max=12, retail_price_max=50.0):
    """Return only candidates that pass the deterministic evidence gate, capped by limit."""
    ready=[]
    for candidate in candidates:
        blockers=evaluate_candidate(candidate, fulfillment_min, fulfillment_max, retail_price_max)
        candidate["blockers"]=blockers
        if not blockers:
            ready.append(candidate)
        if len(ready) >= limit:
            break
    return ready
