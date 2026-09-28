"""Human-readable research report generation."""

from src.models.product import ProductCandidate
from src.validation.product_rules import validate_product


def product_report(product: ProductCandidate) -> str:
    issues = validate_product(product)
    status = "READY FOR TEST" if not issues else "NEEDS LIVE VERIFICATION"

    lines = [
        f"# {product.name}",
        "",
        f"**Status:** {status}",
        f"**Verification:** {product.verification_status}",
        "",
        "## Customer problem",
        product.customer_problem or "Not documented.",
        "",
        "## Demand & trend",
        f"- 12M: {product.trend_12m or 'Not verified'}",
        f"- 5Y: {product.trend_5y or 'Not verified'}",
        f"- Seasonality: {product.seasonality or 'Not verified'}",
        "",
        "## Supplier & fulfillment",
        f"- Supplier: {product.supplier or 'Not verified'}",
        f"- US warehouse: {product.us_warehouse}",
        f"- Delivery: {product.delivery_days or 'Not verified'}",
        "",
        "## Economics",
        f"- Product cost: {product.product_cost}",
        f"- Shipping: {product.shipping_cost}",
        f"- Landed cost: {product.landed_cost}",
        f"- Retail price: {product.retail_price}",
        f"- Gross profit: {product.gross_profit}",
        f"- Gross margin: {product.gross_margin_percent}%",
        "",
        "## Risk & advertising",
        f"- Competition: {product.competition or 'Not verified'}",
        f"- Ad potential: {product.ad_potential or 'Not documented'}",
        f"- Risk: {product.risk or 'Not documented'}",
        "",
        "## Evidence",
    ]

    if product.evidence:
        lines.extend(f"- {item}" for item in product.evidence)
    else:
        lines.append("- No evidence recorded.")

    if issues:
        lines.extend(["", "## Verification blockers"])
        lines.extend(f"- {issue}" for issue in issues)

    return "\n".join(lines)
