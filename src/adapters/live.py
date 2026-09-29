"""Environment-configured live adapters. Credentials are never returned in AdapterResult."""
import os
from datetime import datetime, timezone
from urllib.parse import quote
from .base import AdapterCapabilities, AdapterResult, ResearchAdapter
from .http import get_json, post_json
def _now(): return datetime.now(timezone.utc).isoformat()

class PerplexityAdapter(ResearchAdapter):
    capabilities=AdapterCapabilities("perplexity","web_discovery","web_search",("product discovery","competitor research","source discovery"))
    def research(self, request, request_id):
        key=os.getenv("PERPLEXITY_API_KEY")
        if not key: return AdapterResult.not_connected("perplexity",request_id,"PERPLEXITY_API_KEY is not configured.")
        try:
            data=post_json("https://api.perplexity.ai/chat/completions",{"model":os.getenv("PERPLEXITY_MODEL","sonar"),"messages":[{"role":"user","content":request.get("prompt","Find US dropshipping product opportunities and return sourced findings.")}]},{"Authorization":f"Bearer {key}"})
            return AdapterResult("perplexity","COMPLETE",request_id,_now(),findings=[{"raw_response":data.get("choices",[{}])[0].get("message",{}).get("content","")}])
        except RuntimeError as exc: return AdapterResult("perplexity","BLOCKED",request_id,_now(),unknowns=[str(exc)])

class GeminiAdapter(ResearchAdapter):
    capabilities=AdapterCapabilities("gemini","demand_context","web_search",("demand research","seasonality","market context"))
    def research(self, request, request_id):
        key=os.getenv("GEMINI_API_KEY")
        if not key: return AdapterResult.not_connected("gemini",request_id,"GEMINI_API_KEY is not configured.")
        try:
            model=os.getenv("GEMINI_MODEL","gemini-2.5-flash")
            data=post_json(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",{"contents":[{"parts":[{"text":request.get("prompt","Research demand, seasonality and market context for US dropshipping.")}]}]})
            txt=data.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
            return AdapterResult("gemini","COMPLETE",request_id,_now(),findings=[{"raw_response":txt}])
        except RuntimeError as exc: return AdapterResult("gemini","BLOCKED",request_id,_now(),unknowns=[str(exc)])

class ClaudeAdapter(ResearchAdapter):
    capabilities=AdapterCapabilities("claude","analysis_review","analysis",("contradiction review","risk analysis","competition review"))
    def research(self, request, request_id):
        key=os.getenv("ANTHROPIC_API_KEY")
        if not key: return AdapterResult.not_connected("claude",request_id,"ANTHROPIC_API_KEY is not configured.")
        try:
            data=post_json("https://api.anthropic.com/v1/messages",{"model":os.getenv("ANTHROPIC_MODEL","claude-sonnet-4-6"),"max_tokens":2000,"messages":[{"role":"user","content":request.get("prompt","Review the supplied product research for contradictions, risks and unsupported assumptions.")}]},{"x-api-key":key,"anthropic-version":"2023-06-01"})
            return AdapterResult("claude","COMPLETE",request_id,_now(),findings=[{"raw_response":data.get("content",[{}])[0].get("text","")}])
        except RuntimeError as exc: return AdapterResult("claude","BLOCKED",request_id,_now(),unknowns=[str(exc)])

class CJDropshippingAdapter(ResearchAdapter):
    capabilities=AdapterCapabilities("cj_dropshipping","supplier_validation","supplier_catalog",("supplier","US warehouse","cost","fulfillment"))
    def research(self, request, request_id):
        key=os.getenv("CJ_API_KEY")
        if not key: return AdapterResult.not_connected("cj_dropshipping",request_id,"CJ_API_KEY is not configured.")
        try:
            auth=post_json("https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken",{"apiKey":key})
            token=auth.get("data",{}).get("accessToken")
            if not token: return AdapterResult("cj_dropshipping","BLOCKED",request_id,_now(),unknowns=["CJ authentication did not return an access token."])
            url="https://developers.cjdropshipping.com/api2.0/v1/product/listV2?page=1&size=20"
            keyword=request.get("keyword") or request.get("product_keyword")
            if keyword: url += "&keyWord="+quote(str(keyword))
            data=get_json(url,{"CJ-Access-Token":token})
            return AdapterResult("cj_dropshipping","COMPLETE",request_id,_now(),findings=[{"source":"CJ Product List V2","data":data}],recommended_next_checks=["Query product details and real-time inventory before VERIFIED."])
        except RuntimeError as exc: return AdapterResult("cj_dropshipping","BLOCKED",request_id,_now(),unknowns=[str(exc)])
