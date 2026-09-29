# 🚀 Dropshiping Hub

A beginner-friendly, evidence-first foundation for an AI-assisted USA dropshipping research system.

## Current capabilities

- USA / USD research defaults
- Maximum 5 final candidates
- Retail price cap of $50
- Fulfillment target of 4–12 days
- Evidence gates for supplier, US warehouse, delivery, cost, price, trend, and source fields
- Conflict preservation instead of silent averaging
- CJ Dropshipping live adapter when `CJ_API_KEY` is configured
- Optional Perplexity, Gemini, Claude live adapters
- Optional free Google Trends collection through `pytrends`
- Credential-aware fallback to safe stubs
- Manual GitHub Actions deep-research workflow with downloadable JSON report
- Automated pytest coverage

## Core principles

- Evidence before assumptions
- Quality over quantity
- US-focused research by default
- Prefer reliable suppliers and fast fulfillment
- Avoid fragile, highly technical, sizing-heavy, or high-risk products unless explicitly reviewed
- Never commit API keys or private credentials
- Never treat AI consensus as proof

## How to run deep research

1. Open the repository's **Actions** tab.
2. Select **Deep Research**.
3. Choose **Run workflow**.
4. Optionally enter a product keyword.
5. After the run, download the **research-report** artifact.

The workflow can use `CJ_API_KEY`, plus optional `PERPLEXITY_API_KEY`, `GEMINI_API_KEY`, and `ANTHROPIC_API_KEY` repository secrets. Missing credentials do not create fake evidence.

## Important behavior

The system is allowed to return **zero** final products. A product is not marked VERIFIED merely because an AI model found it. Direct evidence is required for critical supplier/warehouse/fulfillment and other decision fields.

## Project structure

- `.github/workflows/` — automated tests and manual deep research
- `docs/` — operating rules and adapter contracts
- `src/adapters/` — live/stub external research adapters
- `src/pipeline/` — candidate normalization and evidence merging
- `src/workflow/` — deterministic request and evidence gates
- `src/research.py` — end-to-end orchestration
- `tests/` — automated tests

## Status

🟡 **Functional foundation / live research wiring complete.** Final product verification still depends on the availability and quality of live evidence at run time.
