"""Credential-aware connection diagnostics.

This module never returns secret values and never makes network calls.
It only reports whether the local runtime has the configuration needed
to construct each adapter.
"""
from dataclasses import dataclass
import os
from typing import Dict

@dataclass(frozen=True)
class ConnectionStatus:
    name: str
    configured: bool
    credential_name: str
    capabilities: tuple[str, ...] = ()

class ConnectionManager:
    """Inspect adapter configuration without exposing credentials."""

    REQUIREMENTS = {
        "perplexity": ("PERPLEXITY_API_KEY", ("web discovery", "competitor research")),
        "gemini": ("GEMINI_API_KEY", ("demand research", "seasonality", "market context")),
        "claude": ("ANTHROPIC_API_KEY", ("contradiction review", "risk analysis")),
        "cj_dropshipping": ("CJ_API_KEY", ("supplier", "US warehouse", "cost", "fulfillment")),
        "google_trends": ("GOOGLE_TRENDS_ENABLED", ("12M trend", "5Y trend", "seasonality")),
        "tiktok_ads": ("TIKTOK_COMMERCIAL_CONTENT_TOKEN", ("ad evidence", "competition signal")),
    }

    def status(self) -> Dict[str, ConnectionStatus]:
        result = {}
        for name, (credential, capabilities) in self.REQUIREMENTS.items():
            configured = bool(os.getenv(credential, "").strip())
            result[name] = ConnectionStatus(
                name=name,
                configured=configured,
                credential_name=credential,
                capabilities=capabilities,
            )
        return result

    def summary(self) -> list[dict]:
        return [
            {
                "adapter": item.name,
                "status": "CONFIGURED" if item.configured else "NOT_CONFIGURED",
                "credential": item.credential_name,
                "capabilities": list(item.capabilities),
            }
            for item in self.status().values()
        ]
