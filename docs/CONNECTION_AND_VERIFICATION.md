# Connection Manager & Verification Layer

The research engine is designed to work in a free-first configuration. Optional
providers can remain disconnected without causing fake evidence.

## Connection Manager

ConnectionManager checks whether the runtime contains the expected configuration
for each adapter. It never prints or returns secret values and does not make
network calls.

Supported configuration signals:

- CJ_API_KEY
- PERPLEXITY_API_KEY
- GEMINI_API_KEY
- ANTHROPIC_API_KEY
- GOOGLE_TRENDS_ENABLED
- TIKTOK_COMMERCIAL_CONTENT_TOKEN

A configured credential only means configured, not verified. A later live call
can still fail or return incomplete evidence.

## Verification

A candidate can become VERIFIED only when all critical fields are present:

- supplier
- explicit boolean US warehouse evidence
- delivery
- product cost
- shipping cost
- retail price
- 12M trend evidence
- 5Y trend evidence
- source URL
- structured evidence records
- no critical conflicts

AI agreement is never sufficient proof.

## Research lifecycle

Discovery -> Enrichment -> Verification -> Evidence Gate -> Human Review

A disconnected adapter returns BLOCKED/unknown information rather than
inventing data.

## CJ-specific note

CJ current API V2 provides product search, product details, variants,
inventory and freight calculation. Product discovery alone is not enough to
prove US fulfillment or a 4-12 day delivery promise; those fields need direct
warehouse/inventory/logistics evidence before a candidate can be promoted.
