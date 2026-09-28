from src.models.product import ProductCandidate
from src.validation.product_rules import validate_product


def test_margin_calculation():
    product = ProductCandidate(
        name="Test Product",
        product_cost=5,
        shipping_cost=3,
        retail_price=20,
    )
    assert product.landed_cost == 8
    assert product.gross_profit == 12
    assert product.gross_margin_percent == 60


def test_unverified_product_is_flagged():
    product = ProductCandidate(
        name="Test Product",
        customer_problem="Solves a documented problem",
        source_url="https://example.com",
    )
    issues = validate_product(product)
    assert any("not fully verified" in item for item in issues)


def test_high_price_is_flagged():
    product = ProductCandidate(name="Test Product", retail_price=75)
    issues = validate_product(product)
    assert any("above the default $50" in item for item in issues)
