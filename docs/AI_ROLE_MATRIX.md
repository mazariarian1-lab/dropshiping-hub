# AI Role Matrix v1

## Core rule
Each AI is a specialist. No provider is treated as universally best. The workflow manager compares outputs and enforces evidence rules.

| Specialist | Primary role | Secondary role | Must not be trusted blindly for |
|---|---|---|---|
| ChatGPT | Workflow orchestration, synthesis, final structured report | Validation logic, task routing | Unverified live supplier/trend facts |
| Perplexity | Web research and source discovery | Competitor/market research | Supplier inventory or price without first-party evidence |
| Gemini | Broad web/Google ecosystem research | Trend/context research | Treating search summaries as primary evidence |
| Claude | Deep analysis, comparison, contradiction review | Risk analysis, structured reasoning | Creating missing facts |
| Google Trends | Trend evidence | Seasonality/growth signals | Proving sales or profitability |
| CJ Dropshipping | Supplier/product/fulfillment evidence | Cost and warehouse verification | Nothing outside its displayed/source data |
| Shopify | Store/product/commerce execution | Analytics and operations | Product-market validation |
| Canva | Creative production | Ad assets and product visuals | Demand validation |
| Kaching | Bundle/AOV optimization | Quantity breaks/upsell | Product discovery |

## Orchestration sequence
1. Discovery specialists generate a broad candidate pool.
2. Independent research specialists collect evidence.
3. Demand evidence is checked separately.
4. Supplier/fulfillment evidence is checked separately.
5. Claude performs contradiction and risk review.
6. Economics engine calculates deterministic numbers.
7. Workflow manager applies hard gates.
8. Only surviving candidates enter final synthesis.
9. Human approval gates control consequential actions.

## Independence rule
When possible, do not ask every AI to repeat the same question. Give each one a distinct evidence-gathering or validation task.

## Conflict rule
If two sources materially disagree:
- preserve both claims;
- identify the source/date;
- do not average or guess;
- escalate to LIVE VERIFICATION;
- block final approval if the conflict affects a critical decision.
