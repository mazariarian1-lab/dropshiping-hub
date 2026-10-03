from src.adapters import AdapterCapabilities, AdapterResult, build_default_registry

def test_default_registry_contains_all_research_roles():
    registry = build_default_registry()
    assert set(registry) == {"perplexity","gemini","claude","google_trends","cj_dropshipping","tiktok_ads"}

def test_unconnected_adapter_never_fabricates_evidence():
    result = build_default_registry()["cj_dropshipping"].research({"market":"USA"}, "req-001")
    assert result.status == "BLOCKED"
    assert result.candidates == []
    assert result.evidence == []
    assert any("not connected" in item.lower() for item in result.unknowns)

def test_adapter_result_validation_requires_content_for_complete():
    result = AdapterResult("test","COMPLETE","req-1","2026-01-01T00:00:00Z")
    assert "COMPLETE result must contain findings or evidence" in result.validate()

def test_capabilities_are_explicit():
    cap = AdapterCapabilities("google_trends","trend_validation","trend_data",("12M trend","5Y trend"))
    assert cap.live_connected is False
    assert "5Y trend" in cap.capabilities
