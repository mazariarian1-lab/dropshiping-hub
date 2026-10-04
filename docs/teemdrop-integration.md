# TeemDrop integration

## What is connected today

The repository is an evidence-first dropshipping research engine. GitHub Actions can run the research workflow and store report artifacts.

## Important limitation

TeemDrop's current official integration documentation describes authorization of sales stores such as Shopify, eBay, and WooCommerce. It does **not** document a public GitHub connection or public API credentials in the material we can verify. Therefore this repository does not pretend that TeemDrop is already live-connected.

Official TeemDrop guidance:
- Shopify authorization is performed from TeemDrop's Stores flow and redirects to the Shopify App installation.
- Existing store products can be mapped to TeemDrop SKUs inside TeemDrop.

## Safe next step

When TeemDrop provides an API endpoint and credentials for the account, add them as GitHub Actions repository secrets:

- `TEEMDROP_ENABLED=true`
- `TEEMDROP_API_BASE_URL`
- `TEEMDROP_API_KEY`

Never commit the real key to the repository.

The integration should then be implemented as a real adapter using TeemDrop's documented authentication and endpoints. Until those are available, the repository must remain in a non-connected state rather than using guessed endpoints.
