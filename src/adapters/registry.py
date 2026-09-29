"""Default research adapter registry."""
from .base import AdapterCapabilities, ResearchAdapter
from .stub import StubResearchAdapter

DEFAULT_CAPABILITIES = (
    AdapterCapabilities("perplexity","web_discovery","web_search",("product discovery","competitor research","source discovery")),
    AdapterCapabilities("gemini","demand_context","web_search",("demand research","seasonality","market context")),
    AdapterCapabilities("claude","analysis_review","analysis",("contradiction review","risk analysis","competition review")),
    AdapterCapabilities("google_trends","trend_validation","trend_data",("12M trend","5Y trend","seasonality")),
    AdapterCapabilities("cj_dropshipping","supplier_validation","supplier_catalog",("supplier","US warehouse","cost","fulfillment")),
)

def build_default_registry() -> dict[str, ResearchAdapter]:
    return {cap.name: StubResearchAdapter(cap) for cap in DEFAULT_CAPABILITIES}
