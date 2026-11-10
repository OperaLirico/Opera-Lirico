# Workflow efficiency and cadence

This change separates daily monitoring from slower discovery work.

## Daily workflow

- Runs the 29 hand-checked opportunity pages.
- Refreshes a rotating batch of already-registered audition sources.
- Refreshes conservatory admission pages and mirrors selected official PDFs.
- Keeps the last good snapshots when a source is temporarily unavailable.
- Saves only generated website data and PDF snapshots.
- Does not discover new conservatories or audition sources.
- Does not scan LiederNet or automatically append random repertoire records.

The daily push trigger is limited to website assets, data, root Python scripts,
dependencies, and this workflow file. Documentation-only changes and unrelated
repository activity do not start a full scrape/deploy. The schedule and manual
dispatch remain available.

## Weekly discovery workflow

Runs on Monday and can also be started manually. It discovers conservatories
through the existing Wikidata-based candidate process and audition sources
through verified links from known hubs. New candidates are added only after
the existing relevance checks pass. The workflow commits the two source
registries; the next daily run refreshes and publishes the merged snapshots.

The daily source refresher preserves the full registry and replaces only the
rotating batch it actually checked. This prevents unvisited entries from being
silently discarded on each run.

## Dependency cache

Both workflows use setup-python's pip cache keyed by requirements.txt. The
requirements file and package versions are not changed by this optimization.

## Audit cadence

Daily checks are incremental: repository head, open PRs, recent workflow runs,
site availability, changed files, and any failed job logs. Full architecture,
PDF experiment, parser, and data-model reviews are performed weekly or when a
relevant file changes or a failure requires diagnosis.

## Safety

- Official source checks, evidence retention, data validation, and human review remain required.
- No scraper bypass, stealth mode, proxy rotation, login session, or paid service is introduced.
- No PR is merged and no production workflow is changed on main by this PR.