"""Environment-configured live adapters. Credentials are never returned in AdapterResult."""
import json, os
from datetime import datetime, timezone
from urllib.parse import quote
from .base import AdapterCapabilities, AdapterResult, ResearchAdapter
from .http import get_json, post_json

def _now(): return datetime.now(timezone.utc).isoformat()

def _json_candidates(text):
    if not isinstance(text, str): return []
    text=text.strip().replace("```json","").replace("```","").strip()
    try: data=json.loads(text)
    except json.JSONDecodeError: return []
    candidates=data.get("candidates", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    return [c for c in candidates if isinstance(c, dict) and c.get("name")]

def _ai_result(adapter, data, request_id):
    if adapter=="perplexity": text=data.get("choices",[{}])[0].get("message",{}).get("content","")
    elif adapter=="gemini": text=data.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
    else: text=data.get("content",[{}])[0].get("text","")
    return AdapterResult(adapter,"COMPLETE",request_id,_now(),candidates=_json_candidates(text),findings=[{"raw_response":text}],recommended_next_checks=["Validate critical fields with direct evidence before VERIFIED."])

class PerplexityAdapter(ResearchAdapter):
    capabilities=AdapterCapabilities("perplexity","web_discovery","web_search",("product discovery","competitor research","source discovery"))
    def research(self,request,request_id):
        key=os.getenv("PERPLEXITY_API_KEY")
        if not key: return AdapterResult.not_connected("perplexity",request_id,"PERPLEXITY_API_KEY is not configured.")
        try:
            data=post_json("https://api.perplexity.ai/chat/completions",{"model":os.getenv("PERPLEXITY_MODEL","sonar"),"messages":[{"role":"user","content":request.get("prompt","Find US dropshipping product opportunities and return sourced findings.")}]},{"Authorization":f"Bearer {key}"})
            return _ai_result("perplexity",data,request_id)
        except RuntimeError as exc: return AdapterResult("perplexity","BLOCKED",request_id,_now(),unknowns=[str(exc)])

class GeminiAdapter(ResearchAdapter):
    capabilities=AdapterCapabilities("gemini","demand_context","web_search",("demand research","seasonality","market context"))
    def research(self,request,request_id):
        key=os.getenv("GEMINI_API_KEY")
        if not key: return AdapterResult.not_connected("gemini",request_id,"GEMINI_API_KEY is not configured.")
        try:
            model=os.getenv("GEMINI_MODEL","gemini-2.5-flash")
            data=post_json(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",{"contents":[{"parts":[{"text":request.get("prompt","Research demand, seasonality and market context for US dropshipping.")}]}]})
            return _ai_result("gemini",data,request_id)
        except RuntimeError as exc: return AdapterResult("gemini","BLOCKED",request_id,_now(),unknowns=[str(exc)])

class ClaudeAdapter(ResearchAdapter):
    capabilities=AdapterCapabilities("claude","analysis_review","analysis",("contradiction review","risk analysis","competition review"))
    def research(self,request,request_id):
        key=os.getenv("ANTHROPIC_API_KEY")
        if not key: return AdapterResult.not_connected("claude",request_id,"ANTHROPIC_API_KEY is not configured.")
        try:
            data=post_json("https://api.anthropic.com/v1/messages",{"model":os.getenv("ANTHROPIC_MODEL","claude-sonnet-4-6"),"max_tokens":2000,"messages":[{"role":"user","content":request.get("prompt","Review product research for contradictions and unsupported assumptions.")}]},{"x-api-key":key,"anthropic-version":"2023-06-01"})
            return _ai_result("claude",data,request_id)
        except RuntimeError as exc: return AdapterResult("claude","BLOCKED",request_id,_now(),unknowns=[str(exc)])

class CJDropshippingAdapter(ResearchAdapter):
    capabilities=AdapterCapabilities("cj_dropshipping","supplier_validation","supplier_catalog",("supplier","US warehouse","cost","fulfillment"))
    def research(self,request,request_id):
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
            raw=data.get("data",{})
            rows=raw.get("list",[]) if isinstance(raw,dict) else raw if isinstance(raw,list) else []
            candidates=[]
            for row in rows:
                if not isinstance(row,dict): continue
                name=row.get("productName") or row.get("name")
                if not name: continue
                candidates.append({"name":name,"supplier":"CJ Dropshipping","source_url":row.get("productUrl") or row.get("url") or "","product_id":row.get("pid") or row.get("productId"),"product_cost":row.get("sellPrice") or row.get("price")})
            return AdapterResult("cj_dropshipping","COMPLETE",request_id,_now(),candidates=candidates,findings=[{"source":"CJ Product List V2","data":data}],recommended_next_checks=["Query CJ product details, US warehouse inventory, shipping and destination-specific delivery before VERIFIED."])
        except RuntimeError as exc: return AdapterResult("cj_dropshipping","BLOCKED",request_id,_now(),unknowns=[str(exc)])
