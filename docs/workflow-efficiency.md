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
the existing relevance checks pass. The workflow commits the refreshed legacy registry and the pending candidate
queue. Candidate screening is not official-source approval; new candidates
remain pending until a separate evidence review. The next daily run refreshes
the merged source snapshots.

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

## Weekly coverage and silent-miss checks

A separate weekly coverage workflow checks the merged source inventory in
small, resumable batches. It persists a checkpoint containing the inventory
hash, completed source IDs, last result per source and remaining count. It
records HTTP restrictions, extraction failures and normalized text-hash
changes. A changed page or disappearing vocal signal is a review clue, not
proof that a new opportunity exists or that a page is irrelevant.

The weekly audit does not double-count sources_extra.json because sources.json
is the merged registry. Pending candidate URLs are checked separately and are
never promoted by the coverage scan. The monthly institution-coverage review
remains a separate research task; it is not inferred from the weekly URL scan.

## Daily data quality and PDF integrity

The daily workflow writes a read-only opportunity-quality report and a PDF
byte-integrity manifest under .github/audits/. These files are hidden from the
published Pages site. Opportunity records are not silently rewritten by the
report. PDF SHA-256 values establish byte consistency only; publisher
signatures remain unverified unless cryptographic validation is actually done.


## Narrow push triggers

The daily scrape-and-publish workflow is intentionally limited to site assets,
data files and the specific production collection/audit scripts it executes.
It does not run a full scrape for every root-level Python edit, test-only
change, documentation edit or source-coverage-only change. The weekly coverage
workflow has its own trigger for changes to its scanner/workflow and runs after
a successful push-triggered daily workflow, so its full-source scan does not
compete with the daily collector.

Queued push-triggered scrape runs explicitly check out the latest main branch
when they start, rather than the older event SHA. This prevents a delayed run
from starting behind a prior successful scrape commit and creating add/add
conflicts during rebase. If a concurrent main change still causes a genuine
content conflict, the workflow stops rather than force-pushing or overwriting.
