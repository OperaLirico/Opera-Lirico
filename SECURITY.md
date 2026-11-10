# Security Policy

## Reporting a vulnerability

Please do not publish credentials, private data, or an exploitable vulnerability in a public issue. Contact the repository maintainer privately through the contact method listed in the GitHub profile.

## Secrets and sensitive data

- Never commit API keys, passwords, access tokens, private keys, database credentials, or real `.env` files.
- Use GitHub Actions Secrets for automation credentials.
- Use only public, non-sensitive configuration in frontend code. Anything shipped to GitHub Pages is public.
- Never expose a Supabase service-role key in browser JavaScript or a public repository.
- Keep Supabase Row Level Security enabled for tables exposed through client APIs.

## Data collection

- Respect each source website's terms, robots.txt guidance, rate limits, and copyright.
- Do not bypass authentication, CAPTCHAs, paywalls, or access controls.
- Store source URLs and verification timestamps for collected opportunity records.
- Review extracted information before publishing it as authoritative.

## Incident response

If a secret is committed accidentally, revoke or rotate it immediately. Removing it from the latest commit is not sufficient because it may remain in Git history.
