"""Normalize heterogeneous specialist output into one candidate shape."""

from typing import Any

ALIASES = {
    "product_name": "name", "problem": "customer_problem", "customer_need": "customer_problem",
    "supplier_name": "supplier", "warehouse_us": "us_warehouse", "us_warehouse_verified": "us_warehouse",
    "delivery": "delivery_days", "delivery_estimate": "delivery_days", "price": "retail_price",
    "selling_price": "retail_price", "trend_12_month": "trend_12m", "trend_5_year": "trend_5y", "url": "source_url",
}

def normalize_candidate(raw: dict[str, Any]) -> dict[str, Any]:
    """Map common field aliases without inventing values."""
    normalized: dict[str, Any] = {}
    for key, value in raw.items():
        target = ALIASES.get(key, key)
        if value not in (None, ""):
            normalized[target] = value
    normalized.setdefault("status", "RESEARCH CANDIDATE")
    normalized.setdefault("evidence", [])
    normalized.setdefault("unknowns", [])
    normalized.setdefault("conflicts", [])
    normalized.setdefault("blockers", [])
    return normalized
