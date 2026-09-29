"""End-to-end research orchestration without automatic product approval."""
from dataclasses import asdict
from datetime import datetime, timezone
from uuid import uuid4
from .adapters import build_configured_registry
from .workflow import ResearchRequest, ResearchWorkflow

def build_prompt(request):
    return f"""You are a research assistant for USA dropshipping. Find product opportunities, but never invent evidence. Return ONLY JSON with a candidates array. Maximum {request.max_final_candidates * 3} candidates. Required when known: name, customer_problem, trend_12m, trend_5y, source_url. Do not claim CJ US warehouse, delivery, costs, or prices unless directly supported by CJ evidence. Target retail price <= ${request.retail_price_max:g}; target fulfillment {request.fulfillment_min_days}-{request.fulfillment_max_days} days. Prefer non-fragile, non-sized, low-complexity products with clear demonstration/ad potential. Market: USA. Research depth: {request.research_depth}."""

def run_research(request=None,keyword=None):
    request=request or ResearchRequest(); errors=request.validate()
    if errors:return {"status":"INVALID_REQUEST","errors":errors}
    request_id=uuid4().hex; workflow=ResearchWorkflow(request); registry=build_configured_registry(); packets=[]
    base={"market":request.market,"prompt":build_prompt(request)}
    if keyword: base["keyword"]=keyword
    for adapter in registry.values(): packets.append(adapter.research(base,request_id).to_packet())
    workflow.ingest_packets(packets); final=workflow.final_candidates()
    return {"request_id":request_id,"generated_at":datetime.now(timezone.utc).isoformat(),"status":"READY_FOR_HUMAN_REVIEW" if final else "NO_VERIFIED_CANDIDATES","request":asdict(request),"candidates":workflow.state.candidates,"final_candidates":final,"summary":workflow.summary()}
