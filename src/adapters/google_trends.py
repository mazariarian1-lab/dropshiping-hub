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
            if recent.empty or long_term.empty:
                return AdapterResult("google_trends","NO_VALID_FINDINGS",request_id,_now(),unknowns=["Google Trends returned no usable US history for this keyword."])
            def summary(frame):
                series=frame[str(keyword)].dropna()
                vals=[float(x) for x in series.tolist()]
                if not vals: return None
                n=len(vals)
                window=max(1,n//6)
                first_avg=sum(vals[:window])/window
                last_avg=sum(vals[-window:])/window
                change=((last_avg-first_avg)/first_avg*100) if first_avg else None
                peak=max(vals)
                peak_index=vals.index(peak)
                direction="UNKNOWN"
                if change is not None:
                    if change >= 15: direction="GROWING"
                    elif change <= -15: direction="DECLINING"
                    else: direction="STABLE"
                return {"first":vals[0],"last":vals[-1],"peak":peak,"points":n,"first_window_avg":round(first_avg,2),"last_window_avg":round(last_avg,2),"change_percent":round(change,2) if change is not None else None,"direction":direction,"peak_position_percent":round((peak_index/(n-1))*100,1) if n>1 else 0}
            recent_summary=summary(recent); long_summary=summary(long_term)
            candidate={"name":str(keyword),"trend_12m":recent_summary,"trend_5y":long_summary,
                       "evidence":[{"source":"Google Trends via pytrends","keyword":str(keyword),"geo":"US","retrieved_at":_now()}]}
            return AdapterResult("google_trends","COMPLETE",request_id,_now(),candidates=[candidate],findings=[candidate])
        except ImportError:
            return AdapterResult("google_trends","BLOCKED",request_id,_now(),unknowns=["pytrends is not installed; live Google Trends collection is unavailable."])
        except Exception as exc:
            return AdapterResult("google_trends","BLOCKED",request_id,_now(),unknowns=[f"Google Trends request failed: {type(exc).__name__}: {exc}"],recommended_next_checks=["Retry later; Google Trends may rate-limit automated requests."])
