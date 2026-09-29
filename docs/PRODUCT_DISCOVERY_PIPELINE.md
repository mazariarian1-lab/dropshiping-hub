# Product Discovery Pipeline

## Purpose

Convert independent research outputs into one evidence-first candidate set without allowing unsupported claims to become facts.

## Flow

1. **Discovery** — Perplexity/Gemini may produce broad candidates.
2. **Normalization** — field aliases are mapped into the canonical schema. Missing data remains missing.
3. **Merge** — candidates with the same normalized product name are combined.
4. **Evidence preservation** — source-backed evidence is retained rather than overwritten.
5. **Conflict detection** — different values for critical fields are recorded as conflicts.
6. **Verification** — conflicts and missing critical supplier/fulfillment data require live verification.
7. **Economics** — deterministic calculations happen only from supplied cost/price values.
8. **Decision gates** — only candidates satisfying every critical gate can reach the final shortlist.

## Specialist boundaries

- **Perplexity:** discovery, competitor/market research, source discovery.
- **Gemini:** independent demand/trend/context research.
- **Claude:** contradiction, risk, competition and assumption review.
- **Google Trends:** trend evidence only; not proof of sales.
- **CJ Dropshipping:** supplier, warehouse, cost and fulfillment evidence.
- **ChatGPT:** orchestration, normalization, validation, deterministic gates and final synthesis.

## Non-negotiable rules

- AI consensus is not evidence.
- Critical supplier/warehouse/delivery claims require direct or first-party evidence.
- Missing data is UNKNOWN / NEEDS LIVE VERIFICATION.
- Conflicting critical claims block final readiness.
- Never average conflicting supplier, price, delivery or trend claims.
- Final shortlist is capped at 5 and may contain fewer than 5 or zero.
