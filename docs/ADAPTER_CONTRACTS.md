# Research Adapter Contracts

## Purpose
Adapters are the controlled boundary between the workflow and external research systems. They make future live integrations replaceable without changing the evidence gates.

## Current adapters
- Perplexity: web/product discovery, competitor research, source discovery.
- Gemini: demand, seasonality, and market context.
- Claude: contradiction, risk, competition, and assumption review.
- Google Trends: 12M/5Y trend and seasonality evidence.
- CJ Dropshipping: supplier, US warehouse, cost, and fulfillment evidence.

## Safety contract
1. A disconnected adapter returns BLOCKED; it does not fabricate results.
2. Missing evidence stays in unknowns or NEEDS LIVE VERIFICATION.
3. Estimates are allowed only when explicitly supported by a source.
4. Critical supplier, warehouse, and delivery claims require direct or first-party evidence before VERIFIED.
5. Adapter consensus is not proof.
6. Conflicts are preserved and sent to the evidence gate.
7. The adapter layer does not approve products or spend money.

## Result lifecycle
adapter -> AdapterResult -> packet -> merge_packets -> evidence gate -> human review

## Live integration
The current implementation intentionally uses safe stubs. Real connectors can implement ResearchAdapter.research() and return the same AdapterResult shape. No live credential or API key is embedded in source code.
