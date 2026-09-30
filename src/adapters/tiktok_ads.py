"""Optional TikTok Commercial Content evidence adapter."""
import os
from datetime import datetime, timezone
from .base import AdapterCapabilities, AdapterResult
from .http import post_json

CAPABILITIES=AdapterCapabilities("tiktok_ads","ad_validation","tiktok_commercial_content",("ad count","active ads","ad reach","advertiser evidence"))
def _now(): return datetime.now(timezone.utc).isoformat()

class TikTokAdsAdapter:
    capabilities=CAPABILITIES
    def research(self,request,request_id):
        token=os.getenv("TIKTOK_COMMERCIAL_CONTENT_TOKEN")
        if not token: return AdapterResult.not_connected("tiktok_ads",request_id,"TIKTOK_COMMERCIAL_CONTENT_TOKEN is not configured or approved.")
        keyword=request.get("keyword") or request.get("product_keyword")
        if not keyword: return AdapterResult("tiktok_ads","BLOCKED",request_id,_now(),unknowns=["A product keyword is required for TikTok ad research."])
        now=datetime.now(timezone.utc); start=now.replace(year=now.year-1).strftime("%Y%m%d"); end=now.strftime("%Y%m%d")
        fields="ad.id,ad.first_shown_date,ad.last_shown_date,ad.status,ad.reach,advertiser.business_name"
        payload={"filters":{"ad_published_date_range":{"min":start,"max":end},"country_code_list":["US"]},"search_term":str(keyword)[:50],"search_type":"fuzzy_phrase","max_count":10}
        try:
            data=post_json("https://open.tiktokapis.com/v2/research/adlib/ad/query/?fields="+fields,payload,{"Authorization":"Bearer "+token})
            ads=(data.get("data") or {}).get("ads",[]) if isinstance(data,dict) else []; count=len(ads); active=sum(1 for a in ads if str((a.get("ad") or {}).get("status","")).lower()=="active")
            if count>=10: ad_potential,competition="HIGH","HIGH"
            elif count>=3: ad_potential,competition="HIGH","MEDIUM"
            elif count>=1: ad_potential,competition="MEDIUM","LOW"
            else: ad_potential,competition="LOW","LOW"
            candidate={"name":str(keyword),"ad_potential":ad_potential,"competition":competition,"ad_evidence":{"source":"TikTok Commercial Content API","country":"US","matching_ads":count,"active_ads":active,"heuristic":True},"evidence":[{"source":"TikTok Commercial Content API","keyword":str(keyword),"country":"US","matching_ads":count,"active_ads":active}]}
            return AdapterResult("tiktok_ads","COMPLETE",request_id,_now(),candidates=[candidate],findings=[candidate])
        except RuntimeError as exc: return AdapterResult("tiktok_ads","BLOCKED",request_id,_now(),unknowns=[str(exc)])
