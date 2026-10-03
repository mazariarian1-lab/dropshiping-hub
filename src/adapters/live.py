"""Environment-configured live adapters. Credentials are never returned in AdapterResult."""
import json, os, re
from datetime import datetime, timezone
from urllib.parse import quote
from .base import AdapterCapabilities, AdapterResult, ResearchAdapter
from .http import get_json, post_json

def _now(): return datetime.now(timezone.utc).isoformat()

def _json_candidates(text):
    if not isinstance(text, str): return []
    text=text.strip()
    if text.startswith("```"): text=text.replace("```json","").replace("```","").strip()
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

    @staticmethod
    def _number(value):
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        nums=re.findall(r"\\d+(?:[.,]\\d+)?", str(value).replace(",", ""))
        return float(nums[0]) if nums else None

    @staticmethod
    def _price(value):
        if value is None:
            return None
        nums=[float(x) for x in re.findall(r"\\d+(?:[.,]\\d+)?", str(value).replace(",", ""))]
        return round(sum(nums)/len(nums), 2) if nums else None

    @staticmethod
    def _delivery_range(value):
        if value is None:
            return None
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            try:
                return (int(value[0]), int(value[1]))
            except (TypeError, ValueError):
                return None
        nums=[int(x) for x in re.findall(r"\\d+", str(value))]
        if len(nums) >= 2:
            return (min(nums), max(nums))
        if len(nums) == 1:
            return (nums[0], nums[0])
        return None

    def research(self,request,request_id):
        key=os.getenv("CJ_API_KEY")
        if not key:
            return AdapterResult.not_connected("cj_dropshipping",request_id,"CJ_API_KEY is not configured.")
        try:
            auth=post_json("https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken",{"apiKey":key})
            auth_data=auth.get("data") if isinstance(auth,dict) else None
            token=auth_data.get("accessToken") if isinstance(auth_data,dict) else None
            if not token:
                message=(auth.get("message") or auth.get("msg")) if isinstance(auth,dict) else None
                reason="CJ authentication did not return an access token."
                if message:
                    reason += f" Response message: {message}"
                return AdapterResult("cj_dropshipping","BLOCKED",request_id,_now(),unknowns=[reason])

            headers={"CJ-Access-Token":token}
            keyword=request.get("keyword") or request.get("product_keyword")
            url="https://developers.cjdropshipping.com/api2.0/v1/product/listV2?page=1&size=10&countryCode=US&verifiedWarehouse=1"
            if keyword:
                url += "&keyWord="+quote(str(keyword))
            data=get_json(url,headers)
            raw=data.get("data",{}) if isinstance(data,dict) else {}
            rows=[]
            if isinstance(raw,dict):
                if isinstance(raw.get("list"),list):
                    rows=raw["list"]
                elif isinstance(raw.get("content"),list):
                    for block in raw["content"]:
                        if isinstance(block,dict) and isinstance(block.get("productList"),list):
                            rows.extend(block["productList"])
            elif isinstance(raw,list):
                rows=raw

            candidates=[]; findings=[]
            for row in rows:
                if not isinstance(row,dict):
                    continue
                name=row.get("productNameEn") or row.get("productName") or row.get("nameEn") or row.get("name")
                pid=row.get("pid") or row.get("productId") or row.get("id")
                if not name or not pid:
                    continue

                detail=get_json(
                    "https://developers.cjdropshipping.com/api2.0/v1/product/query?pid="+quote(str(pid))+"&countryCode=US",
                    headers,
                )
                dd=detail.get("data",{}) if isinstance(detail,dict) else {}
                if not isinstance(dd,dict):
                    dd={}

                variant_data=get_json(
                    "https://developers.cjdropshipping.com/api2.0/v1/product/variant/query?pid="+quote(str(pid))+"&countryCode=US",
                    headers,
                )
                variants_data=variant_data.get("data",[]) if isinstance(variant_data,dict) else []
                variants=variants_data if isinstance(variants_data,list) else (
                    variants_data.get("list",[]) if isinstance(variants_data,dict) else []
                )
                if not variants:
                    continue

                # Pick a US-stocked variant and independently verify its warehouse inventory.
                selected=None
                selected_inventory=[]
                for v in variants:
                    if not isinstance(v,dict):
                        continue
                    vid=v.get("vid") or v.get("variantId")
                    if not vid:
                        continue
                    stock_data=get_json(
                        "https://developers.cjdropshipping.com/api2.0/v1/product/stock/queryByVid?vid="+quote(str(vid)),
                        headers,
                    )
                    stock_rows=stock_data.get("data",[]) if isinstance(stock_data,dict) else []
                    if not isinstance(stock_rows,list):
                        continue
                    us_rows=[x for x in stock_rows if isinstance(x,dict) and str(x.get("countryCode","")).upper()=="US"]
                    positive=[x for x in us_rows if self._number(x.get("totalInventoryNum",x.get("storageNum"))) and self._number(x.get("totalInventoryNum",x.get("storageNum"))) > 0]
                    if positive:
                        selected=v
                        selected_inventory=positive
                        break
                if selected is None:
                    continue

                vid=selected.get("vid") or selected.get("variantId")
                product_cost=self._price(
                    selected.get("sellPrice") or selected.get("price") or
                    dd.get("sellPrice") or row.get("sellPrice") or row.get("price")
                )
                storage_ids=[str(x.get("areaId") or x.get("storageId") or x.get("stockId")) for x in selected_inventory if x.get("areaId") or x.get("storageId") or x.get("stockId")]
                freight_payload={
                    "startCountryCode":"US",
                    "endCountryCode":"US",
                    "products":[{"quantity":1,"vid":vid}],
                }
                if storage_ids:
                    freight_payload["storageIdList"]=storage_ids
                freight=get_json if False else post_json(
                    "https://developers.cjdropshipping.com/api2.0/v1/logistic/freightCalculate",
                    freight_payload,
                    headers,
                )
                freight_rows=freight.get("data",[]) if isinstance(freight,dict) else []
                if isinstance(freight_rows,dict):
                    freight_rows=freight_rows.get("list",[])
                valid=[]
                for option in freight_rows if isinstance(freight_rows,list) else []:
                    if not isinstance(option,dict):
                        continue
                    price=self._price(option.get("logisticPrice") or option.get("price"))
                    aging=self._delivery_range(option.get("logisticAging") or option.get("aging"))
                    if price is not None and aging and aging[0] >= 0 and aging[1] <= 12:
                        valid.append((price,aging,option))
                if not valid:
                    continue
                shipping_cost,delivery_days,best=min(valid,key=lambda x:x[0])

                inventory_qty=sum(int(self._number(x.get("totalInventoryNum",x.get("storageNum"))) or 0) for x in selected_inventory)
                candidate={
                    "name":name,
                    "supplier":"CJ Dropshipping",
                    "us_warehouse":True,
                    "us_inventory_verified":True,
                    "us_inventory_quantity":inventory_qty,
                    "product_id":pid,
                    "variant_id":vid,
                    "product_sku":dd.get("productSku") or row.get("productSku"),
                    "variant_sku":selected.get("variantSku") or selected.get("sku"),
                    "product_cost":product_cost,
                    "shipping_cost":shipping_cost,
                    "delivery_days":delivery_days,
                    "shipping_method":best.get("logisticName") or best.get("logisticNameEn") or best.get("name"),
                    "shipping_evidence":{
                        "source":"CJ Freight Calculation",
                        "source_type":"first_party",
                        "origin":"US",
                        "destination":"US",
                        "variant_id":vid,
                        "delivery_days":delivery_days,
                        "shipping_cost":shipping_cost,
                    },
                    "source_url":dd.get("supplierLink") or dd.get("productUrl") or row.get("productUrl") or row.get("url") or "",
                    "evidence":[
                        {"source":"CJ Dropshipping API","source_type":"first_party","claim":"product filtered for US inventory","product_id":pid},
                        {"source":"CJ Variant Query","source_type":"first_party","claim":"variant returned with countryCode=US","variant_id":vid},
                        {"source":"CJ Stock Query By VID","source_type":"first_party","claim":"positive US warehouse inventory","variant_id":vid,"inventory_quantity":inventory_qty},
                        {"source":"CJ Freight Calculation","source_type":"first_party","claim":"US-origin to US-destination shipping quote","variant_id":vid,"delivery_days":delivery_days,"shipping_cost":shipping_cost},
                    ],
                }
                candidates.append(candidate)
                findings.append(candidate)

            status="COMPLETE" if candidates else "NO_VALID_FINDINGS"
            unknowns=[] if candidates else ["CJ returned no product variant with independently verified positive US inventory and a valid US-to-US shipping quote within the required delivery target."]
            return AdapterResult("cj_dropshipping",status,request_id,_now(),candidates=candidates,findings=findings,unknowns=unknowns)
        except RuntimeError as exc:
            return AdapterResult("cj_dropshipping","BLOCKED",request_id,_now(),unknowns=[str(exc)])
