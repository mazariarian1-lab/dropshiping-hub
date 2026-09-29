"""Registry for environment-configured live adapters."""
from .base import ResearchAdapter
from .live import PerplexityAdapter, GeminiAdapter, ClaudeAdapter, CJDropshippingAdapter
def build_live_registry() -> dict[str, ResearchAdapter]:
    return {"perplexity":PerplexityAdapter(),"gemini":GeminiAdapter(),"claude":ClaudeAdapter(),"cj_dropshipping":CJDropshippingAdapter()}
