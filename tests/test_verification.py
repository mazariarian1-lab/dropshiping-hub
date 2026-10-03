from src.workflow.verification import verify_candidate

def test_verifier_blocks_incomplete_candidate():
    result = verify_candidate({"name": "Example", "evidence": []})
    assert result["status"] == "NEEDS LIVE VERIFICATION"
    assert result["verification"]["verified"] is False

def test_verifier_never_accepts_non_boolean_us_warehouse():
    candidate = {
        "name": "Example",
        "supplier": "CJ",
        "us_warehouse": "yes",
        "delivery_days": "4-8",
        "product_cost": 5,
        "shipping_cost": 3,
        "retail_price": 24.99,
        "trend_12m": {"direction": "GROWING"},
        "trend_5y": {"direction": "STABLE"},
        "source_url": "https://example.com",
        "evidence": [{"source": "CJ"}],
    }
    result = verify_candidate(candidate)
    assert result["status"] == "NEEDS LIVE VERIFICATION"
    assert result["verification"]["us_warehouse_explicit"] is False

def test_verifier_allows_verified_only_when_critical_fields_are_complete():
    candidate = {
        "name": "Example",
        "supplier": "CJ",
        "us_warehouse": True,
        "delivery_days": "4-8",
        "product_cost": 5,
        "shipping_cost": 3,
        "retail_price": 24.99,
        "trend_12m": {"direction": "GROWING"},
        "trend_5y": {"direction": "STABLE"},
        "source_url": "https://example.com",
        "evidence": [{"source": "CJ", "source_type": "first_party"}],
    }
    result = verify_candidate(candidate)
    assert result["status"] == "VERIFIED"
    assert result["verification"]["verified"] is True
