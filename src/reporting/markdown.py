"""Render evidence-first research results as a human-readable Markdown report."""
from typing import Any, Dict

def _value(value: Any) -> str:
    if value in (None, "", "UNKNOWN", "NEEDS LIVE VERIFICATION"):
        return "UNKNOWN"
    return str(value)

def render_markdown_report(result: Dict[str, Any]) -> str:
    summary = result.get("summary", {})
    candidates = result.get("candidates", [])
    final = result.get("final_candidates", [])
    lines = [
        "# USA Dropshipping Research Report",
        "",
        f"**Status:** {_value(result.get('status'))}",
        f"**Request ID:** {_value(result.get('request_id'))}",
        "",
        "## Summary",
        "",
        f"- Candidates analyzed: {summary.get('candidate_count', 0)}",
        f"- Verified candidates: {summary.get('verified_count', 0)}",
        f"- Final candidates: {summary.get('final_count', 0)}",
        "",
        "## Connection Status",
        "",
        "| Adapter | Status | Capability |",
        "|---|---|---|",
    ]
    for item in result.get("connections", summary.get("connections", [])):
        lines.append(
            f"| {item.get('adapter')} | {item.get('status')} | {', '.join(item.get('capabilities', []))} |"
        )

    lines.extend(["", "## Final Candidates", ""])
    if not final:
        lines.append("**No product passed all evidence gates.**")
    else:
        for index, candidate in enumerate(final, 1):
            lines.extend([
                f"### {index}. {_value(candidate.get('name'))}",
                "",
                f"- Consumer problem: {_value(candidate.get('customer_problem'))}",
                f"- Supplier: {_value(candidate.get('supplier'))}",
                f"- US warehouse: {_value(candidate.get('us_warehouse'))}",
                f"- Delivery: {_value(candidate.get('delivery_days'))}",
                f"- Product cost: {_value(candidate.get('product_cost'))}",
                f"- Shipping: {_value(candidate.get('shipping_cost'))}",
                f"- Retail price: {_value(candidate.get('retail_price'))}",
                f"- Gross margin: {_value(candidate.get('calculated_gross_margin_percent', candidate.get('gross_margin_percent')))}%",
                f"- 12M trend: {_value(candidate.get('trend_growth_signal'))}",
                f"- 5Y trend: {_value(candidate.get('trend_long_term_signal'))}",
                f"- Competition: {_value(candidate.get('competition'))}",
                f"- Ad potential: {_value(candidate.get('ad_potential'))}",
                f"- Risk: {_value(candidate.get('risk_level'))}",
                f"- Evidence status: {_value(candidate.get('status'))}",
                f"- Source: {_value(candidate.get('source_url'))}",
                "",
            ])

    lines.extend(["## Non-final Candidates / Blockers", ""])
    for candidate in candidates:
        if candidate in final:
            continue
        blockers = candidate.get("blockers", [])
        if blockers:
            lines.append(f"- **{_value(candidate.get('name'))}** — {'; '.join(blockers)}")

    lines.extend([
        "",
        "## Safety",
        "",
        "No product is automatically approved for spending, publishing, supplier ordering, or ad launch.",
        "Missing evidence remains UNKNOWN/NEEDS LIVE VERIFICATION.",
    ])
    return "\n".join(lines) + "\n"
