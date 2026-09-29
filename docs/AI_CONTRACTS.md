# AI Research Contracts v1

## Purpose
Define exact input/output contracts so ChatGPT, Perplexity, Gemini, and Claude perform distinct jobs and the Workflow Manager can combine their outputs without duplicated research or invented facts.

## Universal rules
- Output structured evidence, not unsupported conclusions.
- Every factual external claim must include source URL/title and access or publication date when available.
- Never invent product cost, shipping, warehouse, delivery, demand, sales, reviews, trend values, competition, or supplier facts.
- Unknown data must be `UNKNOWN` or `NEEDS LIVE VERIFICATION`.
- Distinguish fact, estimate, inference, and hypothesis.
- Do not treat AI consensus as evidence.
- A source must be appropriate to the claim it supports.
- Critical supplier/fulfillment claims require first-party or directly inspectable evidence before final approval.

## Contract envelope
Every specialist response must contain:
1. `request_id`
2. `role`
3. `status`
4. `candidates[]` or `findings[]`
5. `evidence[]`
6. `unknowns[]`
7. `conflicts[]`
8. `recommended_next_checks[]`
9. `completed_at`

## Evidence object
Each evidence item should contain:
- `claim`
- `value`
- `source`
- `source_type`
- `observed_at`
- `confidence`: HIGH | MEDIUM | LOW
- `verification_state`: VERIFIED | PARTIALLY_VERIFIED | UNVERIFIED
- `notes`

## Status values
`COMPLETE | PARTIAL | BLOCKED | NO_VALID_FINDINGS`

## ChatGPT — Workflow Manager
### Input
ResearchRequest + all upstream specialist outputs.
### Responsibilities
- Normalize the request.
- Route work to specialists.
- Deduplicate candidates.
- Check required fields and evidence.
- Calculate deterministic economics from supplied numbers.
- Apply decision gates.
- Preserve source conflicts.
- Produce the final shortlist of up to 5, including fewer or zero.
### Must not
- Invent missing live facts.
- Override a specialist/source conflict by guessing.
- Treat its own synthesis as primary evidence.
### Output
`FinalResearchPackage`: candidates, gate results, calculations, blockers, evidence map, and human approval requirements.

## Perplexity — Market/Web Research Specialist
### Input
ResearchRequest + candidate discovery task.
### Responsibilities
- Discover candidate products and relevant market/competitor sources.
- Find current product/market pages, competitor offers, pricing examples, reviews, and problem/solution evidence.
- Identify source quality and date.
### Must not
- Claim CJ warehouse, live inventory, supplier cost, or delivery unless directly evidenced.
- Convert search snippets into verified facts.
### Output
For each candidate: problem evidence, market evidence, competitor evidence, source list, uncertainty list, suggested verification checks.

## Gemini — Broad Research & Google-Ecosystem Specialist
### Input
ResearchRequest + candidate list or discovery task.
### Responsibilities
- Perform independent broad research.
- Investigate search demand context, consumer language, seasonal/event context, and relevant Google ecosystem signals where available.
- Cross-check facts discovered by other researchers.
### Must not
- Present search summaries as first-party supplier evidence.
- Treat trend interest as proof of sales.
- Invent exact trend percentages when unavailable.
### Output
Candidate context, demand/trend observations, seasonality/event notes, corroborating sources, contradictions, and unknowns.

## Claude — Deep Analysis & Adversarial Review Specialist
### Input
ResearchRequest + candidate evidence package from other specialists.
### Responsibilities
- Compare evidence and identify contradictions.
- Stress-test consumer need, differentiation, economics, competition, ad potential, operational risk, and policy/IP concerns.
- Identify weak assumptions and missing proof.
- Explain why a candidate should be escalated, rejected, or remain a research candidate without ranking it as a political/electoral judgment.
### Must not
- Manufacture missing evidence.
- Turn weak evidence into certainty.
### Output
Risk review, contradiction map, assumption audit, gate recommendations, and exact next verification steps.

## Orchestration rule
The Workflow Manager should not ask all four AIs the same question. Discovery and web evidence are delegated first; independent cross-checking follows; adversarial review happens after evidence collection; final synthesis happens last.

## Conflict handling
If sources disagree on a critical claim:
- keep both claims;
- record source/date;
- mark the claim CONFLICTED;
- request direct/live verification;
- block final readiness for that claim until resolved.

## Final readiness
A product can enter the final shortlist only if critical evidence gates pass. Interesting but unresolved candidates remain in the research pool.
