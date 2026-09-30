from src.workflow import ResearchRequest, ResearchWorkflow, Stage


def test_default_request_matches_owner_constraints():
    request = ResearchRequest()
    assert request.market == "USA"
    assert request.max_final_candidates == 5
    assert request.retail_price_max == 50
    assert (request.fulfillment_min_days, request.fulfillment_max_days) == (4, 12)
    assert request.allow_zero_results is True
    assert request.validate() == []


def test_workflow_does_not_fill_missing_evidence():
    workflow = ResearchWorkflow(ResearchRequest())
    workflow.state.candidates = [
        {"status": "RESEARCH_CANDIDATE", "blockers": []},
        {"status": "VERIFIED", "blockers": ["warehouse unresolved"]},
    ]
    assert workflow.final_candidates() == []
    assert workflow.state.stage == Stage.EVIDENCE_GATE


def test_verified_unblocked_candidate_can_pass():
    workflow = ResearchWorkflow(ResearchRequest())
    workflow.state.candidates = [{
        "status": "VERIFIED",
        "supplier": "Test Supplier",
        "us_warehouse": True,
        "delivery_days": (4, 8),
        "product_cost": 5.0,
        "shipping_cost": 4.0,
        "shipping_evidence": {"source": "CJ Freight Calculation", "destination": "US"},
        "retail_price": 24.99,
        "trend_12m": "growing",
        "trend_5y": "stable",
        "source_url": "https://example.com/product",
        "gross_margin_percent": 63.96,
        "blockers": [],
    }]
    assert len(workflow.final_candidates()) == 1
    assert workflow.state.stage == Stage.FINAL


def test_ingest_packets_merges_candidates_before_gating():
    workflow = ResearchWorkflow(ResearchRequest())
    state = workflow.ingest_packets([{
        "candidates": [{"product_name": "Cable Organizer", "price": 19.99}]
    }])
    assert state.stage == Stage.EVIDENCE_GATE
    assert state.candidates[0]["name"] == "Cable Organizer"
    assert state.candidates[0]["retail_price"] == 19.99


def test_request_rejects_non_usa_or_non_us_warehouse_configuration():
    request = ResearchRequest(market="Canada", preferred_warehouse="CA")
    errors = request.validate()
    assert "market must be USA" in errors
    assert "preferred_warehouse must remain US" in errors


def test_gate_calculates_landed_cost_and_margin():
    workflow = ResearchWorkflow(ResearchRequest())
    workflow.state.candidates = [{
        "status":"VERIFIED","supplier":"CJ Dropshipping","us_warehouse":True,
        "delivery_days":(4,8),"product_cost":5.0,"shipping_cost":4.0,
        "retail_price":24.99,"trend_12m":"growing","trend_5y":"stable",
        "source_url":"https://example.com/product","gross_margin_percent":63.99,
    }]
    final = workflow.final_candidates()
    assert len(final) == 1
    assert final[0]["landed_cost"] == 9.0
    assert final[0]["calculated_gross_margin_percent"] == 63.99

def test_gate_rejects_missing_shipping_even_when_product_cost_exists():
    workflow = ResearchWorkflow(ResearchRequest())
    workflow.state.candidates = [{
        "status":"VERIFIED","supplier":"CJ Dropshipping","us_warehouse":True,
        "delivery_days":(4,8),"product_cost":5.0,"retail_price":24.99,
        "trend_12m":"growing","trend_5y":"stable","source_url":"https://example.com/product",
    }]
    assert workflow.final_candidates() == []

def test_merge_preserves_cj_identity_and_flags_conflicting_ids():
    workflow = ResearchWorkflow(ResearchRequest())
    state = workflow.ingest_packets([
        {"candidates": [{"product_name": "Cable Organizer", "product_id": "CJ-1", "variant_id": "V-1"}]},
        {"candidates": [{"product_name": "Cable Organizer", "product_id": "CJ-2", "variant_id": "V-2"}]},
    ])
    assert len(state.candidates) == 1
    assert state.candidates[0]["status"] == "NEEDS LIVE VERIFICATION"
    assert any(x["field"] == "product_id" for x in state.candidates[0]["conflicts"])


def test_verified_candidates_are_scored_and_sorted():
    workflow = ResearchWorkflow(ResearchRequest())
    base = {"status":"VERIFIED","supplier":"CJ Dropshipping","us_warehouse":True,"delivery_days":(4,8),"product_cost":5.0,"shipping_cost":4.0,"retail_price":24.99,"trend_12m":"growing","trend_5y":"stable","trend_growth_signal":"GROWING","trend_long_term_signal":"GROWING","seasonality_signal":True,"shipping_evidence":{"source":"CJ Freight Calculation","destination":"US"},"source_url":"https://example.com/product"}
    workflow.state.candidates = [dict(base, name="A"), dict(base, name="B", retail_price=20.0, product_cost=7.0, shipping_cost=5.0, trend_growth_signal="STABLE")]
    final = workflow.final_candidates()
    assert [x["name"] for x in final] == ["A", "B"]
    assert final[0]["product_score"] > final[1]["product_score"]
