"""Best-effort Google Trends adapter with explicit evidence limits."""
import os
from datetime import datetime, timezone
from .base import AdapterCapabilities, AdapterResult
CAPABILITIES=AdapterCapabilities("google_trends","trend_validation","trend_data",("12M trend","5Y trend","seasonality"))
def _now(): return datetime.now(timezone.utc).isoformat()
class GoogleTrendsAdapter:
    capabilities=CAPABILITIES
    def research(self,request,request_id):
        if os.getenv("GOOGLE_TRENDS_ENABLED","").strip().lower() not in {"1","true","yes"}:
            return AdapterResult.not_connected("google_trends",request_id,"GOOGLE_TRENDS_ENABLED is not enabled; no live trend data was collected.")
        keyword=request.get("keyword") or request.get("product_keyword")
        if not keyword:
            return AdapterResult("google_trends","BLOCKED",request_id,_now(),unknowns=["A product keyword is required for Google Trends."],recommended_next_checks=["Provide keyword/product_keyword and retry."])
        try:
            from pytrends.request import TrendReq
            p=TrendReq(hl="en-US",tz=0,timeout=(10,30))
            p.build_payload([str(keyword)],timeframe="today 12-m",geo="US"); recent=p.interest_over_time()
            p.build_payload([str(keyword)],timeframe="today 5-y",geo="US"); long_term=p.interest_over_time()
            if recent.empty or long_term.empty: return AdapterResult("google_trends","NO_VALID_FINDINGS",request_id,_now(),unknowns=["Google Trends returned no usable US history for this keyword."])
            def summary(frame):
                vals=frame[str(keyword)].dropna().tolist()
                return {"first":float(vals[0]),"last":float(vals[-1]),"peak":float(max(vals)),"points":len(vals)} if vals else None
            return AdapterResult("google_trends","COMPLETE",request_id,_now(),findings=[{"keyword":str(keyword),"geo":"US","trend_12m":summary(recent),"trend_5y":summary(long_term),"source":"Google Trends via pytrends","retrieved_at":_now()}])
        except ImportError: return AdapterResult("google_trends","BLOCKED",request_id,_now(),unknowns=["pytrends is not installed; live Google Trends collection is unavailable."])
        except Exception as exc: return AdapterResult("google_trends","BLOCKED",request_id,_now(),unknowns=[f"Google Trends request failed: {type(exc).__name__}: {exc}"],recommended_next_checks=["Retry later; Google Trends may rate-limit automated requests."])
