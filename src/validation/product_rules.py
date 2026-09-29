"""Deterministic product validation rules.

These rules identify missing evidence and operational risks; they do not predict success.
"""

from src.models.product import ProductCandidate

FULFILLMENT_MIN_DAYS = 4
FULFILLMENT_MAX_DAYS = 12
DEFAULT_MAX_PRICE = 50.0
DEFAULT_MIN_MARGIN = 40.0


def validate_product(product: ProductCandidate) -> list[str]:
    issues: list[str] = []
    if not product.name.strip(): issues.append("Missing product name.")
    if not product.customer_problem.strip(): issues.append("Customer problem is not documented.")
    if not product.source_url.strip(): issues.append("No source URL recorded.")
    if product.verification_status != "VERIFIED": issues.append("Supplier/product evidence is not fully verified.")
    if product.us_warehouse is not True: issues.append("US warehouse is not verified as available.")
    if product.retail_price is not None and product.retail_price > DEFAULT_MAX_PRICE: issues.append("Retail price is above the default $50 research threshold.")
    if product.gross_margin_percent is not None and product.gross_margin_percent < DEFAULT_MIN_MARGIN: issues.append("Gross margin is below the default 40% screening threshold.")
    if product.delivery_days and not any(token in product.delivery_days for token in ("4-12", "4–12")):
        issues.append("Delivery does not explicitly match the default 4-12 day target.")
    return issues
