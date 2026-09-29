"""Safe non-live adapter used until a real connector is configured."""
from .base import AdapterCapabilities, AdapterResult, ResearchAdapter

class StubResearchAdapter(ResearchAdapter):
    def __init__(self, capabilities: AdapterCapabilities):
        self.capabilities = capabilities

    def research(self, request: dict, request_id: str) -> AdapterResult:
        return AdapterResult.not_connected(
            self.capabilities.name, request_id,
            f"{self.capabilities.name} is not connected; no live research was performed and no claims were generated.",
        )
