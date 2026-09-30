from src.research import build_prompt, run_research
from src.workflow import ResearchRequest
from src.adapters.base import AdapterResult


def test_prompt_contains_owner_constraints():
    prompt = build_prompt(ResearchRequest())
    assert "USA" in prompt and "<= $50" in prompt and "4-12" in prompt and "never invent evidence" in prompt


def test_research_without_credentials_is_safe(monkeypatch):
    for key in ["PERPLEXITY_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", "CJ_API_KEY", "GOOGLE_TRENDS_ENABLED"]:
        monkeypatch.delenv(key, raising=False)
    result = run_research(ResearchRequest())
    assert result["status"] == "NO_VERIFIED_CANDIDATES"
    assert result["final_candidates"] == []


def test_live_checks_run_after_discovery(monkeypatch):
    class FakeAdapter:
        def __init__(self, name):
            self.name = name

        def research(self, request, request_id):
            if self.name == "discovery":
                return AdapterResult(
                    "discovery", "COMPLETE", request_id, "now",
                    candidates=[{"name": "Cable Organizer", "customer_problem": "cable clutter"}],
                )
            if self.name == "google_trends":
                assert request["keyword"] == "Cable Organizer"
                return AdapterResult(
                    "google_trends", "COMPLETE", request_id, "now",
                    candidates=[{"name": "Cable Organizer", "trend_12m": "growing", "trend_5y": "stable"}],
                )
            if self.name == "cj_dropshipping":
                assert request["keyword"] == "Cable Organizer"
                return AdapterResult(
                    "cj_dropshipping", "COMPLETE", request_id, "now",
                    candidates=[{"name": "Cable Organizer", "supplier": "CJ Dropshipping", "source_url": "https://example.com"}],
                )
            return AdapterResult(self.name, "BLOCKED", request_id, "now")

    registry = {
        "discovery": FakeAdapter("discovery"),
        "cj_dropshipping": FakeAdapter("cj_dropshipping"),
        "google_trends": FakeAdapter("google_trends"),
    }
    monkeypatch.setattr("src.research.build_configured_registry", lambda: registry)
    result = run_research(ResearchRequest())
    candidate = next(c for c in result["candidates"] if c["name"] == "Cable Organizer")
    assert candidate["trend_12m"] == "growing"
    assert candidate["supplier"] == "CJ Dropshipping"
    assert candidate["status"] == "RESEARCH CANDIDATE"
    assert result["final_candidates"] == []
