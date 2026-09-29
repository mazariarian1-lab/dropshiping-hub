# Quality Control and Anti-Hallucination Protocol v1

## Before research
- Normalize request.
- Record all constraints.
- Create a unique research run ID.
- Define the date/time of the run.

## During research
- Save source URL for material claims.
- Record source type and checked time.
- Separate facts, estimates, hypotheses and opinions.
- Preserve conflicting evidence instead of smoothing it over.
- Prefer first-party/current evidence for supplier and fulfillment claims.

## Before final report
Run these checks:
1. Is every final candidate under the retail ceiling?
2. Is fulfillment evidence present?
3. Is supplier evidence present?
4. Are cost and shipping inputs evidenced?
5. Are trend claims sourced?
6. Is customer need explicit?
7. Is ad potential explained?
8. Are risk flags complete?
9. Are calculations deterministic?
10. Are unsupported claims excluded?
11. Are final candidates actually better-supported than rejected candidates?
12. If fewer than five pass, did the system correctly return fewer than five?

## Prohibited behavior
- Inventing URLs
- Inventing sales numbers
- Inventing CJ warehouse status
- Inventing delivery times
- Inventing reviews
- Inventing trend percentages
- Calling estimates verified
- Filling missing values just to complete a table
- Treating AI consensus as evidence
- Treating trend growth as guaranteed demand
- Treating gross margin as net profit
- Claiming a product will definitely sell

## Final report language
Use precise labels:
- VERIFIED
- PARTIALLY VERIFIED
- ESTIMATE
- RESEARCH CANDIDATE
- NEEDS LIVE VERIFICATION
- REJECTED

The system should be conservative when evidence is weak.
