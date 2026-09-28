from src.models.product import ProductCandidate
from src.research.screen import screen_candidate


def test_candidate_with_missing_supplier_evidence_is_not_ready():
    product = ProductCandidate(
        name="Example",
        us_warehouse=True,
        verification_status="NEEDS LIVE VERIFICATION",
        retail_price=25,
        product_cost=5,
        shipping_cost=3,
    )
    ready, reasons = screen_candidate(product)
    assert not ready
    assert any("evidence" in reason.lower() for reason in reasons)


def test_candidate_with_verified_economics_can_pass():
    product = ProductCandidate(
        name="Example",
        us_warehouse=True,
        verification_status="VERIFIED",
        retail_price=25,
        product_cost=5,
        shipping_cost=3,
    )
    ready, reasons = screen_candidate(product)
    assert ready
    assert reasons == []
