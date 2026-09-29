# Research Adapter Contracts

## Purpose
Adapters are the controlled boundary between the workflow and external research systems. They keep live integrations replaceable without changing the deterministic evidence gates.

## Adapters
- Perplexity: product discovery and source discovery when `PERPLEXITY_API_KEY` is configured.
- Gemini: demand and seasonality context when `GEMINI_API_KEY` is configured.
- Claude: contradiction/risk review when `ANTHROPIC_API_KEY` is configured.
- Google Trends: free `pytrends`-based 12M/5Y US trend collection when `GOOGLE_TRENDS_ENABLED=true`.
- CJ Dropshipping: catalog discovery when `CJ_API_KEY` is configured.

## Safety contract
1. A disconnected adapter returns BLOCKED; it does not fabricate results.
2. Missing evidence stays in unknowns or NEEDS LIVE VERIFICATION.
3. AI responses are accepted as candidates only when valid JSON is returned; malformed output is ignored.
4. Critical supplier, warehouse, delivery, cost, price and trend claims require direct evidence before VERIFIED.
5. Adapter consensus is not proof.
6. Conflicts are preserved and sent to the evidence gate.
7. The adapter layer never approves products or spends money.

## End-to-end lifecycle
adapter -> AdapterResult -> candidate normalization -> merge_packets -> deterministic evidence gate -> human review

## Manual deep research
GitHub Actions contains a **Deep Research** workflow. Run it manually from the Actions tab. It accepts an optional product keyword and stores `research-report.json` as an artifact. The workflow can use the existing `CJ_API_KEY` secret and optional AI secrets without ever printing their values.

## Important limitation
A live connection does **not** automatically make a product VERIFIED. The system intentionally returns zero final products when critical evidence is missing or conflicting. This is expected behavior and protects against hallucinated supplier, warehouse, delivery, trend, or margin claims.
