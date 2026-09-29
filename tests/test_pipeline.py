from src.pipeline import merge_packets, normalize_candidate


def test_normalization_maps_common_aliases_without_inventing_data():
    result = normalize_candidate({"product_name": "Cable Organizer", "price": 19.99})
    assert result["name"] == "Cable Organizer"
    assert result["retail_price"] == 19.99
    assert "supplier" not in result


def test_merge_preserves_critical_conflicts():
    result = merge_packets([
        {"candidates": [{"name": "Example", "delivery": "4-7 days", "source_url": "https://a.example"}]},
        {"candidates": [{"name": "Example", "delivery": "8-12 days", "source_url": "https://b.example"}]},
    ])
    assert len(result) == 1
    assert result[0]["status"] == "NEEDS LIVE VERIFICATION"
    assert any(item["field"] == "delivery_days" for item in result[0]["conflicts"])
