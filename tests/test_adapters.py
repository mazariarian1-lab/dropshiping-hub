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


def test_cj_adapter_requires_positive_us_inventory_and_uses_us_freight(monkeypatch):
    from src.adapters.live import CJDropshippingAdapter

    monkeypatch.setenv("CJ_API_KEY", "test-key")
    calls = []

    def fake_post(url, payload, headers=None, timeout=30):
        calls.append(("POST", url, payload))
        if "authentication" in url:
            return {"data": {"accessToken": "token"}}
        assert "freightCalculate" in url
        assert payload["startCountryCode"] == "US"
        assert payload["endCountryCode"] == "US"
        return {"data": [{"logisticPrice": "4.50", "logisticAging": "4-7", "logisticName": "US Local"}]}

    def fake_get(url, headers=None, timeout=30):
        calls.append(("GET", url))
        if "listV2" in url:
            assert "countryCode=US" in url
            assert "verifiedWarehouse=1" in url
            return {"data": {"content": [{"productList": [{"pid": "p1", "productNameEn": "Cable Organizer", "sellPrice": "3.00"}]}]}}
        if "product/query" in url:
            assert "countryCode=US" in url
            return {"data": {"productSku": "SKU-1", "supplierLink": "https://cj.example/p1"}}
        if "variant/query" in url:
            assert "countryCode=US" in url
            return {"data": [{"vid": "v1", "variantSku": "VSKU-1", "sellPrice": "3.00"}]}
        if "stock/queryByVid" in url:
            return {"data": [{"countryCode": "US", "totalInventoryNum": 12, "areaId": "US-1"}]}
        raise AssertionError(f"Unexpected GET URL: {url}")

    monkeypatch.setattr("src.adapters.live.post_json", fake_post)
    monkeypatch.setattr("src.adapters.live.get_json", fake_get)

    result = CJDropshippingAdapter().research({"keyword": "cable organizer"}, "req-1")

    assert result.status == "COMPLETE"
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate["us_warehouse"] is True
    assert candidate["us_inventory_verified"] is True
    assert candidate["us_inventory_quantity"] == 12
    assert candidate["shipping_cost"] == 4.5
    assert candidate["delivery_days"] == (4, 7)
    assert any(item["source"] == "CJ Stock Query By VID" for item in candidate["evidence"])
