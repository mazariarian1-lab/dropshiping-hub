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
    capabilities=AdapterCapabilities("cj_dropshipping","supplier_validation","supplier_catalog",("supplier","US warehouse","cost","fulfillment","inventory"))

    def research(self,request,request_id):
        key=os.getenv("CJ_API_KEY")
        if not key:
            return AdapterResult.not_connected("cj_dropshipping",request_id,"CJ_API_KEY is not configured.")
        try:
            auth=post_json("https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken",{"apiKey":key})
            token=auth.get("data",{}).get("accessToken")
            if not token:
                return AdapterResult("cj_dropshipping","BLOCKED",request_id,_now(),unknowns=["CJ authentication did not return an access token."])

            headers={"CJ-Access-Token":token}
            keyword=request.get("keyword") or request.get("product_keyword")
            url="https://developers.cjdropshipping.com/api2.0/v1/product/listV2?page=1&size=10&countryCode=US&verifiedWarehouse=1"
            if keyword:
                url += "&keyWord="+quote(str(keyword))
            data=get_json(url,headers)
            raw=data.get("data",{})
            rows=raw.get("list",[]) if isinstance(raw,dict) else raw if isinstance(raw,list) else []
            candidates=[]
            findings=[]
            for row in rows:
                if not isinstance(row,dict):
                    continue
                name=row.get("productNameEn") or row.get("productName") or row.get("name")
                pid=row.get("pid") or row.get("productId")
                if not name:
                    continue

                candidate={
                    "name":name,
                    "supplier":"CJ Dropshipping",
                    "us_warehouse":True,
                    "source_url":row.get("productUrl") or row.get("url") or "",
                    "product_id":pid,
                    "product_cost":row.get("sellPrice") or row.get("price"),
                }
                if row.get("deliveryCycle") is not None:
                    candidate["delivery_days"]=row.get("deliveryCycle")

                # Product detail gives a stronger identity and supplier link when available.
                if pid:
                    detail=get_json("https://developers.cjdropshipping.com/api2.0/v1/product/query?pid="+quote(str(pid)),headers)
                    detail_data=detail.get("data",{}) if isinstance(detail,dict) else {}
                    if isinstance(detail_data,dict):
                        candidate["product_sku"]=detail_data.get("productSku") or detail_data.get("sku")
                        candidate["source_url"]=detail_data.get("supplierLink") or detail_data.get("productUrl") or candidate["source_url"]
                        candidate["product_cost"]=detail_data.get("sellPrice") or candidate.get("product_cost")
                        candidate["delivery_days"]=detail_data.get("deliveryCycle") or candidate.get("delivery_days")

# Exact variant + USA freight evidence; never infer shipping.
variant_data=get_json("https://developers.cjdropshipping.com/api2.0/v1/product/variant/query?pid="+quote(str(pid)),headers)
variants=variant_data.get("data",{}).get("list",[]) if isinstance(variant_data.get("data",{}),dict) else []
if variants:
    v=variants[0]
    candidate["variant_id"]=v.get("vid") or v.get("variantId")
    candidate["variant_sku"]=v.get("variantSku") or v.get("sku")
    candidate["variant_cost"]=v.get("sellPrice") or v.get("price") or candidate.get("product_cost")
vid=candidate.get("variant_id")
if vid:
    freight=post_json("https://developers.cjdropshipping.com/api2.0/v1/logistic/freightCalculate",{"startCountryCode":"CN","endCountryCode":"US","products":[{"quantity":1,"vid":vid}]},headers)
    rows=freight.get("data",[]) if isinstance(freight,dict) else []
    usable=[x for x in rows if isinstance(x,dict) and x.get("logisticPrice") is not None]
    if usable:
        valid=[]
        for option in usable:
            aging=option.get("logisticAging")
            if isinstance(aging,(list,tuple)) and len(aging)>=2:
                lo,hi=int(aging[0]),int(aging[1])
            elif isinstance(aging,(int,float)):
                lo=hi=int(aging)
            else:
                import re
                nums=[int(x) for x in re.findall(r"\\d+",str(aging or ""))]
                lo,hi=(min(nums),max(nums)) if len(nums)>=2 else (nums[0],nums[0]) if nums else (None,None)
            if lo is not None and hi is not None and lo>=4 and hi<=12:
                option=dict(option); option["_delivery_days"]=(lo,hi); valid.append(option)
        if valid:
            best=min(valid,key=lambda x:float(x.get("logisticPrice",0)))
            candidate["shipping_cost"]=float(best["logisticPrice"])
            candidate["delivery_days"]=best["_delivery_days"]
            candidate["shipping_method"]=best.get("logisticName")
            candidate["shipping_evidence"]={"source":"CJ Freight Calculation","destination":"US","variant_id":vid,"delivery_days":candidate["delivery_days"]}
        else:
            candidate["unknowns"].append("CJ returned no USA shipping option within the required 4-12 day delivery window.")
    else: candidate["unknowns"].append("CJ returned no usable USA freight option for this variant.")

                    inventory=get_json("https://developers.cjdropshipping.com/api2.0/v1/product/stock/getInventoryByPid?pid="+quote(str(pid)),headers)
                    inventory_data=inventory.get("data",{}) if isinstance(inventory,dict) else {}
                    inventories=inventory_data.get("inventories",[]) if isinstance(inventory_data,dict) else []
                    us_rows=[x for x in inventories if isinstance(x,dict) and str(x.get("areaEn","")).lower()=="us warehouse"]
                    candidate["us_inventory_verified"]=bool(us_rows)
                    candidate["us_inventory_quantity"]=sum(int(x.get("totalInventory",0) or 0) for x in us_rows if str(x.get("totalInventory","")).isdigit())

                candidate["evidence"]=[{"source":"CJ Dropshipping API","warehouse_filter":"US","verifiedWarehouse":1,"product_id":pid}]
                candidate.setdefault("unknowns",[]).append("Destination-specific USA shipping requires a valid CJ freight result.")
                candidates.append(candidate)
                findings.append(candidate)

            return AdapterResult("cj_dropshipping","COMPLETE",request_id,_now(),
                                 candidates=candidates,findings=findings,
                                 recommended_next_checks=["Calculate destination-specific freight and delivery before VERIFIED."])
        except RuntimeError as exc:
            return AdapterResult("cj_dropshipping","BLOCKED",request_id,_now(),unknowns=[str(exc)])
