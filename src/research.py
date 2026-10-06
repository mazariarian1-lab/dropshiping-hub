"""End-to-end evidence-first research orchestration without automatic product approval."""
from dataclasses import asdict
from datetime import datetime, timezone
from uuid import uuid4

from .adapters import build_configured_registry
from .adapters.connection_manager import ConnectionManager
from .workflow import ResearchRequest, ResearchWorkflow

def build_prompt(request, role="discovery", candidates=None):
    base = f"""USA dropshipping research. Evidence first; never invent facts.
Market: USA. Research depth: {request.research_depth}.
Owner constraints: retail <= ${request.retail_price_max:g}; fulfillment target {request.fulfillment_min_days}-{request.fulfillment_max_days} days;
prefer CJ Dropshipping US Warehouse, non-fragile, non-sized, non-complex, non-medical/therapeutic products.
Consumer problem and ad/demo potential are required. Trend evidence must cover 12M and 5Y when available.
Return ONLY JSON with a candidates array. Use UNKNOWN when evidence is unavailable.
"""
    if role == "discovery":
        return base + f"""Find up to {request.max_final_candidates * 3} promising evergreen or seasonal product opportunities for US dropshipping.
Focus on clear consumer problems, giftability where relevant, healthy economics, visual demonstration potential, and low operational risk.
Do not claim CJ stock, warehouse, SKU, delivery, exact cost or shipping unless directly sourced from CJ.
"""
    if role == "review":
        names = [c.get("name") for c in (candidates or []) if c.get("name")]
        return base + """You are the independent critical reviewer.
Review ONLY the supplied candidates. Do not invent new candidates.
For each candidate, identify evidence-supported strengths, weaknesses, competition, ad potential, risks, contradictions and missing proof.
Preserve uncertainty. Return one candidate object per supplied product name.
Candidates:
""" + json.dumps(names, ensure_ascii=False) + """
"""
    return base
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
    summary["connections"] = ConnectionManager().summary()
    return {
        "request_id": request_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_HUMAN_REVIEW" if final else "NO_VERIFIED_CANDIDATES",
        "request": asdict(request),
        "connections": summary["connections"],
        "candidates": workflow.state.candidates,
        "final_candidates": final,
        "summary": summary,
    }
