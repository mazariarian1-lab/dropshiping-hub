# AI Input/Output Contract Examples v1

## Standard ResearchRequest

```json
{
  "request_id": "generated-id",
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
  "evidence_first": true
}
```

## Candidate evidence packet

```json
{
  "candidate_id": "cand-001",
  "product_name": "Example Product",
  "customer_problem": {"claim": "...", "evidence_ids": ["ev-001"]},
  "demand": {"claim": "...", "evidence_ids": ["ev-002"]},
  "trend_12m": {"value": "UNKNOWN", "evidence_ids": []},
  "trend_5y": {"value": "UNKNOWN", "evidence_ids": []},
  "supplier": {"name": "CJ Dropshipping", "evidence_ids": []},
  "warehouse_us": {"value": "UNKNOWN", "evidence_ids": []},
  "delivery_days": {"value": "UNKNOWN", "evidence_ids": []},
  "economics": {
    "product_cost": "UNKNOWN",
    "shipping": "UNKNOWN",
    "landed_cost": "UNKNOWN",
    "retail_price": "UNKNOWN"
  },
  "competition": {"value": "UNKNOWN", "evidence_ids": []},
  "ad_potential": {"value": "UNKNOWN", "evidence_ids": []},
  "risks": [],
  "blockers": []
}
```

## Specialist response examples

### Perplexity
Return candidate discovery and web evidence. Do not fill supplier/warehouse fields unless a first-party source supports them.

### Gemini
Return independent demand, seasonality, consumer-language, and Google-ecosystem context. Exact trend values must be sourced or marked unknown.

### Claude
Return contradiction/risk analysis over the evidence packet. It may calculate or reason from provided facts, but must not create missing facts.

### ChatGPT
Return the normalized final package after applying gates. It must show which claims are verified, estimated, unresolved, or conflicted.

## Never use
- `confidence = 100%`
- invented URLs
- invented supplier stock
- invented sales volume
- invented Google Trends values
- invented delivery promises
- "AI consensus" as evidence
