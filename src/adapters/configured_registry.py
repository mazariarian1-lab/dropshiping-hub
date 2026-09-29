"""Build a safe registry that uses live adapters only when credentials are present."""
import os
from .registry import DEFAULT_CAPABILITIES
from .stub import StubResearchAdapter
from .live import PerplexityAdapter, GeminiAdapter, ClaudeAdapter, CJDropshippingAdapter
from .google_trends import GoogleTrendsAdapter
LIVE_BUILDERS={"perplexity":PerplexityAdapter,"gemini":GeminiAdapter,"claude":ClaudeAdapter,"cj_dropshipping":CJDropshippingAdapter,"google_trends":GoogleTrendsAdapter}
REQUIRED_KEYS={"perplexity":"PERPLEXITY_API_KEY","gemini":"GEMINI_API_KEY","claude":"ANTHROPIC_API_KEY","cj_dropshipping":"CJ_API_KEY","google_trends":"GOOGLE_TRENDS_ENABLED"}
def build_configured_registry():
    registry={}
    for cap in DEFAULT_CAPABILITIES:
        key=REQUIRED_KEYS[cap.name]
        if os.getenv(key," ").strip(): registry[cap.name]=LIVE_BUILDERS[cap.name]()
        else: registry[cap.name]=StubResearchAdapter(cap)
    return registry
