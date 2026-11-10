# Italia Audizioni engineering roadmap: P0–P5

This roadmap separates implemented controls from work that still requires real-world validation. A passing workflow is not, by itself, proof that every source was checked or every parser is accurate.

## P0 — Source and opportunity trust

**Status: core foundation implemented; ongoing data review remains.**

Acceptance:
- New discovery URLs enter a pending candidate queue.
- Legacy source records retain review labels and last-known snapshots.
- Failed refreshes do not erase last-good extracts.
- Published opportunities require official publisher, verified review and published status, with first-party evidence.
- Opportunity dates are separate and timezone-aware.

Evidence: docs/source-review-policy.md, docs/opportunity-data-policy.md, data/opportunity.schema.json, tests/.

## P1 — Reliable collection and quality control

**Status: baseline safeguards implemented; operational coverage audit added.**

Acceptance:
- HTTP, restriction and extraction failures are distinguishable.
- Last-good snapshots survive transient failures.
- Daily opportunity quality report counts expiry, missing links, stale verification and invalid dates.
- Automated tests cover data contracts and failure preservation.
- Source scans record errors rather than silently treating them as zero new opportunities.

Limitations: the current main collector still uses a fixed Scrapling source list plus a rotating discovered-source refresh. Per-domain fetch policy tuning and deeper retry/timeout metrics remain future improvements.

## P2 — Per-source multi-engine strategy

**Status: first five-source pilot completed; source-specific strategy decisions pending.**

The source policy registry records the current Scrapling path for every registered URL and explicitly marks alternatives as unassessed. The first five-source pilot checks robots.txt, advertised feeds and sitemaps, and compares Scrapling, lxml and Trafilatura on identical raw HTML. It remains evaluation-only pending review of the measured results.

Acceptance:
- Each source has an evidence-based preferred method and fallback.
- API/RSS/sitemap/public JSON is preferred when available and permitted.
- HTTP + lxml/parsel, Scrapling, curl_cffi and Playwright are introduced only where a representative test proves a real advantage.
- A comparison report records accuracy, field completeness, runtime, dependency and maintenance cost.

No blanket dependency expansion is permitted. Current production requirements remain intentionally small.

## P3 — Change tracking and silent-miss detection

**Status: first operational layer implemented; requires repeated weekly cycles to establish baselines.**

Acceptance:
- All registered sources and pending candidates are covered on a weekly cycle, in resumable batches.
- A persistent checkpoint records inventory hash, completed source IDs, results and remaining count.
- Normalized page-text hashes detect content changes.
- A previously accessible page becoming inaccessible, extraction becoming empty, or a previously visible vocal signal disappearing is flagged.
- A successful scan never implies opportunity completeness or publisher authenticity.

The first complete scan creates the baseline; trend-based anomaly detection becomes more meaningful after multiple completed cycles.

## P4 — Main-text extraction quality

**Status: first offline snapshot comparison completed; corrected link-retention comparison in progress.**

Acceptance:
- Compare the existing extraction with Trafilatura on the same offline HTML snapshots.
- Test retention of title, dates, links, tables, role/voice type, eligibility, fees and application deadlines.
- Keep Trafilatura only if it improves main-text completeness without losing structured details.

A separate evaluation workflow captured five representative official pages as raw HTML artifacts and compared Scrapling, lxml full text and Trafilatura on identical bytes. First-pass character counts showed Trafilatura can be substantially shorter on list-heavy pages and longer on some content pages; this is not an accuracy verdict. The first report incorrectly repeated DOM link counts across parser rows, so a second pass now measures whether each parser's text actually retains relevant DOM anchor labels and separately counts Trafilatura Markdown links. Trafilatura remains evaluation-only and is not added to production requirements. Acceptance requires manual review of notice/date/role/eligibility/fee/link/table retention.

## P5 — Evidence integrity and isolated PDF automation

**Status: integrity baseline implemented; digital signatures and Docling extraction remain unverified.**

Acceptance:
- Mirrored PDF files have a manifest with source record, local path, size, PDF-byte validation and SHA-256.
- SHA-256 is described only as byte-integrity evidence.
- Publisher signatures are marked verified only after cryptographic validation against a trusted publisher certificate/key.
- PDF extraction is isolated, page-grounded and tested on representative official PDFs.
- Machine extraction remains pending manual review and cannot publish records.

The current implementation adds a PDF integrity manifest and an isolated Docling evaluation protocol. No publisher signature has been verified, and no Docling output is promoted into production.

## Completion policy

P0–P5 are engineering workstreams, not a claim that the whole platform is finished. P2 and P4 require measured source-level evidence; P3 requires repeated weekly runs; P5 signature and parser acceptance require real signed PDFs and representative samples. Report these as pending until their evidence exists.
