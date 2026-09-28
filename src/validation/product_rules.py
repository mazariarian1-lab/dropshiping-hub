"""Deterministic product validation rules.

These rules do not decide whether a product will succeed.
They identify missing evidence and operational risks.
"""

from src.models.product import ProductCandidate


def validate_product(product: ProductCandidate) -> list[str]:
    issues: list[str] = []

    if not product.name.strip():
        issues.append("Missing product name.")

    if not product.customer_problem.strip():
        issues.append("Customer problem is not documented.")

    if not product.source_url.strip():
        issues.append("No source URL recorded.")

    if product.verification_status != "VERIFIED":
        issues.append("Supplier/product evidence is not fully verified.")

    if product.us_warehouse is not True:
        issues.append("US warehouse is not verified as available.")

    if product.retail_price is not None and product.retail_price > 50:
        issues.append("Retail price is above the default $50 research threshold.")

    if product.gross_margin_percent is not None and product.gross_margin_percent < 40:
        issues.append("Gross margin is below the default 40% screening threshold.")

    if product.delivery_days and "3-8" not in product.delivery_days and "3–8" not in product.delivery_days:
        issues.append("Delivery does not explicitly match the default 3-8 day target.")

    return issues
