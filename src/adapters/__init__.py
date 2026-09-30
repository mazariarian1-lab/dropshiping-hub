"""Evidence-safe research adapter contracts and built-in adapter stubs."""
from .base import AdapterCapabilities, AdapterResult, ResearchAdapter
from .stub import StubResearchAdapter
from .registry import build_default_registry
__all__ = ["AdapterCapabilities","AdapterResult","ResearchAdapter","StubResearchAdapter","build_default_registry","build_configured_registry"]

from .live_registry import build_live_registry

from .configured_registry import build_configured_registry
