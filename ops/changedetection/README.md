# OperaLab source monitoring (changedetection.io)

This is an optional, self-hosted companion service for detecting changes on official conservatory, opera-house, competition, and masterclass pages.

## Why it is separate

OperaLab is published as a static GitHub Pages site. changedetection.io is a persistent server application and cannot run inside GitHub Pages or a GitHub Actions runner as a continuously available service. Run it on a small always-on machine/VPS with Docker Compose. Do not add it to the public site bundle.

The existing Scrapling + GitHub Actions collection remains the source-of-truth publishing pipeline. This service is an **early-warning layer**: it identifies pages/PDFs that may have changed. A detected change must still pass OperaLab's existing extraction, source-policy, evidence, and human-verification rules before public data is updated.

## Start locally

Requirements: Docker Engine and the Docker Compose plugin.

```bash
cd ops/changedetection
docker compose up -d
docker compose ps
```

Open http://127.0.0.1:5000 on the host machine. The port is bound to loopback only and the datastore is persistent in a named Docker volume.

## Security and operating notes

- Do not expose port 5000 directly to the public internet. If remote access is needed, use an authenticated HTTPS reverse proxy or a private VPN such as Tailscale.
- Keep the datastore volume backed up; it contains watch definitions and service state.
- Start with a small allowlisted set of official source URLs. Respect each source's terms, robots.txt, rate limits, and access controls; do not bypass logins, CAPTCHAs, or blocks.
- Use conservative polling intervals (start at 24 hours for admissions pages; less frequent for stable pages). Avoid aggressive parallel checks.
- Start with the default HTTP fetcher. Enable a browser fetcher only for pages that demonstrably require JavaScript and after reviewing resource/security implications.
- LLM features are disabled in this Compose profile to avoid unexpected API costs and sending source content to a third-party model.
- A change alert is not proof of a new audition or an open application. Re-run the official-source verification and date/status checks before publication.
- No webhook or automatic publication is enabled in this first integration. This prevents an unreviewed page diff from entering the public site.

## Initial pilot

1. Start the service.
2. Add 5–10 official URLs selected from the existing source registry.
3. Set a 24-hour check interval and monitor title/body changes.
4. Compare alerts with the next scheduled OperaLab scrape.
5. Only after the pilot shows reliable signals, design a controlled export/notification bridge to the existing GitHub Actions workflow.

## Upstream

- https://github.com/dgtlmoon/changedetection.io
- License: Apache-2.0 (verify upstream license when upgrading).
