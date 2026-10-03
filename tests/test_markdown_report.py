from src.reporting.markdown import render_markdown_report

def test_markdown_report_handles_zero_results():
    result = {
        "status": "NO_VERIFIED_CANDIDATES",
        "request_id": "req-1",
        "summary": {"candidate_count": 2, "verified_count": 0, "final_count": 0},
        "connections": [],
        "candidates": [{"name": "Example", "blockers": ["US warehouse is not verified"]}],
        "final_candidates": [],
    }
    report = render_markdown_report(result)
    assert "No product passed all evidence gates." in report
    assert "US warehouse is not verified" in report

def test_markdown_report_contains_verified_candidate_details():
    candidate = {
        "name": "Cable Organizer",
        "customer_problem": "Cable clutter",
        "supplier": "CJ Dropshipping",
        "us_warehouse": True,
        "delivery_days": (4, 8),
        "product_cost": 4,
        "shipping_cost": 3,
        "retail_price": 24.99,
        "gross_margin_percent": 71.99,
        "trend_growth_signal": "GROWING",
        "trend_long_term_signal": "STABLE",
        "competition": "MEDIUM",
        "ad_potential": "HIGH",
        "risk_level": "LOW",
        "status": "VERIFIED",
        "source_url": "https://example.com",
        "blockers": [],
    }
    report = render_markdown_report({
        "status": "READY_FOR_HUMAN_REVIEW",
        "request_id": "req-2",
        "summary": {"candidate_count": 1, "verified_count": 1, "final_count": 1},
        "connections": [],
        "candidates": [candidate],
        "final_candidates": [candidate],
    })
    assert "Cable Organizer" in report
    assert "US warehouse" in report
    assert "GROWING" in report
