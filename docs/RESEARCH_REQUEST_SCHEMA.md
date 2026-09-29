# Research Request Schema v1

{
  "market": "USA",
  "currency": "USD",
  "research_depth": "deep",
  "max_final_candidates": 5,
  "allow_fewer_than_max": true,
  "allow_zero_results": true,
  "product_types": ["evergreen", "seasonal"],
  "retail_price_max": 50,
  "fulfillment_target_days": {"min": 4, "max": 12},
  "preferred_supplier": "CJ Dropshipping",
  "preferred_warehouse": "US",
  "consumer_problem_required": true,
  "trend_windows": ["12M", "5Y"],
  "ad_potential_required": true,
  "fragile_products": "avoid",
  "complex_electronics": "avoid",
  "sizing_heavy_products": "avoid",
  "medical_claim_products": "avoid",
  "evidence_first": true,
  "deep_research_over_speed": true,
  "automation_level": "high_with_human_approval_for_material_actions"
}

## Missing-input rule
If a required research parameter is absent, use the configured default only when the default is explicitly defined here. Otherwise ask the user.

## Output contract
Every candidate must include evidence and verification status. Every calculation must expose its inputs.
