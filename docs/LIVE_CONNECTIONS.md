# Live Connections

The project now has environment-configured live adapters for Perplexity, Gemini, Claude and CJ Dropshipping.

Required environment variables:
- PERPLEXITY_API_KEY
- GEMINI_API_KEY
- ANTHROPIC_API_KEY
- CJ_API_KEY

Google Trends is intentionally not faked. Its official API is currently an Alpha program, so a verified client should only be enabled after access is granted.

CJ authentication uses the CJ API key to obtain an access token, then Product List V2. Product details and real-time inventory must be queried before supplier or warehouse claims become VERIFIED.

Security:
- Never commit real keys.
- Never put keys in research packets or logs.
- Never paste keys into chat.
- Rotate exposed keys immediately.

The adapter layer itself is free; provider pricing and access requirements are external and can change.