"""Candidate screening utilities."""

from src.models.product import ProductCandidate

DEFAULT_MAX_PRICE = 50.0
DEFAULT_MIN_MARGIN = 40.0


def screen_candidate(product: ProductCandidate, max_price: float = DEFAULT_MAX_PRICE, min_margin: float = DEFAULT_MIN_MARGIN) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if product.retail_price is not None and product.retail_price > max_price:
        reasons.append(f"Retail price exceeds {max_price:.0f} USD.")

    if product.gross_margin_percent is not None and product.gross_margin_percent < min_margin:
        reasons.append(f"Gross margin is below {min_margin:.0f}%.")

    if product.us_warehouse is not True:
        reasons.append("US warehouse is not verified.")

    if product.verification_status != "VERIFIED":
        reasons.append("Critical product/supplier evidence is not verified.")

    return len(reasons) == 0, reasons
