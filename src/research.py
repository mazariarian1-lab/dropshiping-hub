"""End-to-end evidence-first research orchestration without automatic product approval."""
from dataclasses import asdict
from datetime import datetime, timezone
from uuid import uuid4

from .adapters import build_configured_registry
from .workflow import ResearchRequest, ResearchWorkflow

def build_prompt(request):
    return f"""You are a research assistant for USA dropshipping. Find product opportunities, but never invent evidence.
Return ONLY JSON with a candidates array. Maximum {request.max_final_candidates * 3} candidates.
For each candidate provide, when actually evidenced: name, customer_problem, source_url, supplier, us_warehouse,
delivery_days, product_cost, shipping_cost, retail_price, gross_margin_percent, trend_12m, trend_5y,
competition, ad_potential, risk_level, and evidence/source details.
Do not claim CJ US warehouse, exact SKU availability, delivery, costs, shipping, prices, or trend values
unless directly supported by the relevant source. Target retail price <= ${request.retail_price_max:g};
target fulfillment {request.fulfillment_min_days}-{request.fulfillment_max_days} days.
Prefer non-fragile, non-sized, low-complexity products solving a clear consumer problem with demonstration/ad potential.
Competition and ad_potential must be evidence-backed; if unavailable, use UNKNOWN rather than guessing. Risk_level must explain concrete product risks.
If TikTok Commercial Content evidence is available, use it as a secondary ad/competition signal, not as proof of profitability.
Market: USA. Research depth: {request.research_depth}. Evidence > assumptions."""

def _name_key(value):
    return " ".join(str(value or "").lower().replace("-", " ").split())

def _similar(a, b):
    aa = set(_name_key(a).split())
    bb = set(_name_key(b).split())
    if not aa or not bb:
        return False
    overlap = len(aa & bb) / max(1, min(len(aa), len(bb)))
    return overlap >= 0.55

def _enrich_with_live_checks(candidates, registry, request_id, limit):
    """Run CJ + Google Trends against discovered product names, without upgrading status."""
    packets = []
    for candidate in candidates[:limit]:
        name = candidate.get("name")
        if not name:
            continue
        context = {"market": "USA", "keyword": name, "product_keyword": name}
        for adapter_name in ("cj_dropshipping", "google_trends", "tiktok_ads"):
            adapter = registry.get(adapter_name)
            if adapter is None:
                continue
            result = adapter.research(context, request_id)
            packet = result.to_packet()
            packet["discovery_name"] = name
            packets.append(packet)
    return packets

def run_research(request=None, keyword=None):
    request = request or ResearchRequest()
    errors = request.validate()
    if errors:
        return {"status": "INVALID_REQUEST", "errors": errors}
    request_id = uuid4().hex
    workflow = ResearchWorkflow(request)
    registry = build_configured_registry()
    base = {"market": request.market, "prompt": build_prompt(request)}
    if keyword:
        base["keyword"] = keyword

    # Discovery first. CJ is a fallback only when independent discovery adapters return nothing.
    discovery_adapters = [
        adapter for name, adapter in registry.items()
        if name not in {"cj_dropshipping", "google_trends"}
    ]
    packets = [adapter.research(base, request_id).to_packet() for adapter in discovery_adapters]
    discovery_candidates = []
    for packet in packets:
        discovery_candidates.extend(packet.get("candidates", []))

    # With only CJ configured, the supplier catalog can safely provide discovery candidates.
    if not discovery_candidates:
        cj = registry.get("cj_dropshipping")
        if cj is not None:
            cj_packet = cj.research(base, request_id).to_packet()
            packets.append(cj_packet)
            discovery_candidates.extend(cj_packet.get("candidates", []))

    if keyword and not any(_similar(keyword, c.get("name")) for c in discovery_candidates):
        discovery_candidates.append({"name": keyword})

    packets.extend(_enrich_with_live_checks(
        discovery_candidates, registry, request_id, request.max_final_candidates * 3
    ))
    workflow.ingest_packets(packets)
    final = workflow.final_candidates()
    adapter_diagnostics = [
        {
            "adapter": packet.get("adapter"),
            "status": packet.get("status"),
            "unknowns": packet.get("unknowns", []),
        }
        for packet in packets
        if packet.get("status") not in {"COMPLETE"} or packet.get("unknowns")
    ]
    summary = workflow.summary()
    summary["adapter_diagnostics"] = adapter_diagnostics
    return {
        "request_id": request_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_HUMAN_REVIEW" if final else "NO_VERIFIED_CANDIDATES",
        "request": asdict(request),
        "candidates": workflow.state.candidates,
        "final_candidates": final,
        "summary": summary,
    }
