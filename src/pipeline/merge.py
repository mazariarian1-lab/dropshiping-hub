"""Merge independent specialist packets without treating consensus as proof."""

from collections import defaultdict
from typing import Any, Iterable
from .normalize import normalize_candidate

CRITICAL_FIELDS = {"supplier", "us_warehouse", "delivery_days", "product_cost", "shipping_cost", "retail_price", "trend_12m", "trend_5y", "source_url", "product_id", "variant_id"}

def _identity(candidate: dict[str, Any]) -> str:
    return " ".join(str(candidate.get("name", "")).lower().strip().split())

def merge_packets(packets: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge by normalized product name while treating CJ product/variant IDs as identity evidence."""
    merged: dict[str, dict[str, Any]] = {}
    observations: dict[str, dict[str, list[Any]]] = defaultdict(lambda: defaultdict(list))
    for packet in packets:
        for raw in packet.get("candidates", []):
            candidate = normalize_candidate(raw)
            key = _identity(candidate)
            if not key:
                continue
            target = merged.setdefault(key, {"name": candidate.get("name", ""), "status": "RESEARCH CANDIDATE", "evidence": [], "unknowns": [], "conflicts": [], "blockers": []})
            for field, value in candidate.items():
                if field in {"name", "status", "evidence", "unknowns", "conflicts", "blockers"}:
                    continue
                if field in CRITICAL_FIELDS:
                    observations[key][field].append(value)
                elif field not in target:
                    target[field] = value
            target["evidence"].extend(x for x in candidate.get("evidence", []) if x not in target["evidence"])
            # Preserve exact CJ identity separately so similarly named products cannot silently substitute for each other.
            if candidate.get("product_id") and not target.get("product_id"):
                target["product_id"] = candidate["product_id"]
            if candidate.get("variant_id") and not target.get("variant_id"):
                target["variant_id"] = candidate["variant_id"]
            target["unknowns"].extend(x for x in candidate.get("unknowns", []) if x not in target["unknowns"])
    for key, target in merged.items():
        for field, values in observations[key].items():
            distinct = list(dict.fromkeys(values))
            if len(distinct) == 1:
                target[field] = distinct[0]
            elif len(distinct) > 1:
                target["conflicts"].append({"field": field, "values": distinct})
                target["unknowns"].append(f"Resolve conflicting evidence for {field}.")
        if target["conflicts"]:
            target["status"] = "NEEDS LIVE VERIFICATION"
    return list(merged.values())
