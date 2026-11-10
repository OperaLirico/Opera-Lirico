# Source Monitoring

Reserved for lightweight source-change tracking.

## Planned use

Track whether selected official source pages have changed since the previous check, then produce a review signal for the existing collection process.

## Initial approach

- Prefer HTTP metadata or normalized content fingerprints where permitted.
- Record source URL, check time, and change status.
- Respect source terms, robots.txt guidance, and rate limits.
- Avoid storing full copies of third-party pages unless permitted.
- Keep monitoring failures separate from successful 'no change' results.

The existing scheduled scraper remains unchanged. This directory does not deploy a persistent monitoring server.
