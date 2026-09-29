from src.workflow import ResearchRequest, ResearchWorkflow, Stage

def test_default_request_matches_owner_constraints():
    request = ResearchRequest()
    assert request.market == "USA"
    assert request.max_final_candidates == 5
    assert request.retail_price_max == 50
    assert (request.fulfillment_min_days, request.fulfillment_max_days) == (4, 12)
    assert request.allow_zero_results is True

def test_workflow_does_not_fill_missing_evidence():
    workflow = ResearchWorkflow(ResearchRequest())
    workflow.state.candidates = [
        {"status": "RESEARCH_CANDIDATE", "blockers": []},
        {"status": "VERIFIED", "blockers": ["warehouse unresolved"]},
    ]
    assert workflow.final_candidates() == []

def test_verified_unblocked_candidate_can_pass():
    workflow = ResearchWorkflow(ResearchRequest())
    workflow.state.candidates = [{"status": "VERIFIED", "blockers": []}]
    assert len(workflow.final_candidates()) == 1
