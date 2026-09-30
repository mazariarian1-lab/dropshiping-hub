from src.workflow.gates import evaluate_candidate, ready_candidates


def verified_candidate():
    return {
        "status": "VERIFIED",
        "supplier": "CJ Dropshipping",
        "us_warehouse": True,
        "delivery_days": "4-12 days",
        "product_cost": 4.0,
        "shipping_cost": 3.0,
        "retail_price": 24.99,
        "trend_12m": "source-backed",
        "customer_problem": "solves a clear problem",
        "ad_potential": "HIGH",
        "risk_level": "LOW",
        "shipping_evidence": {"destination": "US"},
        "trend_5y": "source-backed",
        "source_url": "https://example.com/product",
        "gross_margin_percent": 71.99,
    }


def test_verified_complete_candidate_passes():
    assert evaluate_candidate(verified_candidate()) == []


def test_conflict_blocks_candidate():
    candidate = verified_candidate()
    candidate["conflicts"] = [{"field": "delivery_days"}]
    assert "critical evidence conflict exists" in evaluate_candidate(candidate)


def test_four_to_twelve_is_the_target():
    candidate = verified_candidate()
    candidate["delivery_days"] = "3-8 days"
    assert any("4-12" in item for item in evaluate_candidate(candidate))


def test_ready_candidates_are_capped():
    candidates = [verified_candidate() for _ in range(7)]
    assert len(ready_candidates(candidates, limit=5)) == 5
