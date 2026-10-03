"""Evidence verification and promotion rules.

The verifier is deliberately conservative: it can preserve or downgrade
evidence, but it never upgrades a candidate to VERIFIED from AI consensus alone.
"""
from typing import Any, Dict

CRITICAL_FIELDS = (
    "supplier",
    "us_warehouse",
    "delivery_days",
    "product_cost",
    "shipping_cost",
    "retail_price",
    "trend_12m",
    "trend_5y",
    "source_url",
)

def _missing(value: Any) -> bool:
    return value in (None, "", "UNKNOWN", "NEEDS LIVE VERIFICATION")

def verify_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy with conservative verification metadata."""
    out = dict(candidate)
    blockers = list(dict.fromkeys(out.get("blockers", [])))
    conflicts = out.get("conflicts") or []
    evidence = out.get("evidence") or []

    if conflicts:
        blockers.append("critical evidence conflict exists")

    for field in CRITICAL_FIELDS:
        if _missing(out.get(field)):
            blockers.append(f"missing critical evidence: {field}")

    if out.get("us_warehouse") is not True:
        blockers.append("US warehouse is not explicitly verified")

    if not evidence:
        blockers.append("no structured evidence records are attached")

    if blockers:
        out["status"] = "NEEDS LIVE VERIFICATION"
    else:
        out["status"] = "VERIFIED"

    out["blockers"] = list(dict.fromkeys(blockers))
    out["verification"] = {
        "critical_fields_complete": not any(_missing(out.get(f)) for f in CRITICAL_FIELDS),
        "us_warehouse_explicit": out.get("us_warehouse") is True,
        "conflict_free": not bool(conflicts),
        "structured_evidence_present": bool(evidence),
        "verified": out["status"] == "VERIFIED",
    }
    return out

def verify_candidates(candidates: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return [verify_candidate(candidate) for candidate in candidates]
