# Italia Audizioni engineering roadmap: P0–P5

Last evidence-based status update: 10 November 2026.

This roadmap separates implemented controls from work that still requires real-world validation. A passing workflow is not, by itself, proof that every source was checked or every parser is accurate.

## P0 — Source and opportunity trust

**Status: core foundation implemented; ongoing data review remains.**

Acceptance:
- New discovery URLs enter a pending candidate queue.
- Legacy source records retain review labels and last-known snapshots.
- Failed refreshes do not erase last-good extracts.
- Published opportunities require official publisher, verified review and published status, with first-party evidence.
- Opportunity dates are separate and timezone-aware.

Current evidence:
- Structured opportunity registry contains 7 published, verified, official records.
- A new Teatro Massimo public selection for two Contralto roles was discovered from its official job-opening sitemap and added with the official announcement and PDF.
- The application deadline is 4 December 2026 at 12:00 Europe/Rome.
- The official page says the audition begins 19 December; the official PDF says 20 December. The structured audition date is intentionally omitted and the conflict is shown in the public card notes.
- Front-end cards display notes and a separate official PDF link.

Evidence: docs/source-review-policy.md, docs/opportunity-data-policy.md, data/opportunity.schema.json, data/opportunities.json, tests/.

## P1 — Reliable collection and quality control

**Status: baseline safeguards and structured link capture implemented; first production refresh is validating the new link fields.**

Acceptance:
- HTTP, restriction and extraction failures are distinguishable.
- Last-good snapshots survive transient failures.
- Daily opportunity quality report counts expiry, missing links, stale verification and invalid dates.
- Automated tests cover data contracts and failure preservation.
- Source scans record errors rather than silently treating them as zero new opportunities.
- Source snapshots preserve full bounded page text and relevant first-party link evidence.

Current evidence:
- Production snapshots now include page_text, relevant_links, relevant_links_total and relevant_links_truncated.
- Each relevant link stores an absolute URL and visible label; aria-label/title are retained for icon-only controls.
- At most 1,000 links are stored per page. If the total exceeds the cap, an explicit truncation flag is set. The 10 November production refresh verified 29/29 active sources had page_text and relevant_links metadata, with truncated=false for all 29; the 15 legacy_unreviewed records are not counted as active coverage.
- Last-good snapshot preservation includes structured links.
- The first full daily production refresh after this change is being used to verify actual per-source link coverage and truncation.

Limitations: per-domain timeout/retry tuning and structured link quality review across all sources remain ongoing.

## P2 — Per-source multi-engine strategy

**Status: first three source-specific assessment batches completed (15/44); 29 sources remain baseline_only.**

Batch 1 assessed Teatro alla Scala, Teatro Carlo Felice, Teatro Massimo, AsLiCo and Morlacchi. Batch 2 assessed:
- Teatro Regio Torino: Scrapling retained; sitemap yielded 48 vocal/audition keyword-match URLs.
- Teatro dell'Opera di Roma Fabbrica: Scrapling retained; sitemap children yielded no page URLs; public API root inspected without querying guessed routes. The checked page was a closed/historical call, not an open opportunity.
- Teatro Verdi Trieste: Scrapling retained; sitemap XML was invalid and feeds had no relevant entries.
- Teatro La Fenice: Scrapling retained; sitemap yielded 27 keyword-match URLs; public API root returned HTTP 403 and was not bypassed.
- Teatro Lirico di Cagliari: Scrapling retained; sitemap yielded nine keyword-match URLs; public API root was inspected without querying guessed routes; feeds had no relevant entries.

Batch 3 assessed:
- Teatro Comunale di Bologna: Scrapling retained; sitemap yielded one keyword-match URL among the first five child maps; Trafilatura preserved only 135/441 exact relevant href targets.
- Maggio Musicale Fiorentino: direct HTML retained; common sitemap endpoints returned 404 (not an access-control rule).
- Teatro Lirico Sperimentale di Spoleto: Scrapling retained; sitemap yielded 140 keyword-match URLs and an advertised feed had three relevant entries; API root inspected without querying guessed routes.
- Accademia d'Arte Lirica Osimo: direct HTML retained; sitemap endpoints returned 404, feeds had no relevant entries, and the advertised API root was inspected without querying guessed routes.
- Valsesia Musica: Scrapling retained; sitemap yielded four keyword-match URLs.

Across all three batches, Scrapling remains the production fetch method. Sitemap and, for Spoleto, the advertised feed are secondary discovery channels where useful; no production engine was automatically switched. Measured results and decisions are stored in data/source_fetch_policies.json and archived under reports/p2/source-strategy-batch-1-2026-11-10.*, batch-2-2026-11-10.* and batch-3-2026-11-10.*. The .github/audits/extraction-pilot-latest.md file represents only the latest batch and is not the permanent archive. Across tested pages, Trafilatura is not promoted as the default. lxml full-text often includes substantial boilerplate; Scrapling retained more relevant anchor labels on most pages, while some Trafilatura Markdown outputs preserved a subset of exact href targets. Structured href targets are evaluated separately from flattened text.

Acceptance:
- Each source has an evidence-based preferred method and fallback.
- API/RSS/sitemap/public JSON is preferred when available and permitted.
- HTTP + lxml/parsel, Scrapling, curl_cffi and Playwright are introduced only where a representative test proves a real advantage.
- A comparison report records accuracy, field completeness, runtime, dependency and maintenance cost.

No blanket dependency expansion is permitted. Current production requirements remain intentionally small.

## P3 — Change tracking and silent-miss detection

**Status: first complete 44/44 weekly coverage scan succeeded; cross-week anomaly detection awaits another full cycle.**

Current evidence:
- The latest complete weekly scan checked all 44 registered sources, with 0 fetch failures and 0 remaining sources.
- The first complete scan establishes a baseline; it does not prove that no historical changes were missed.
- Source coverage now has a concurrency group independent from daily refresh and source discovery.
- Pages deployment also has its own concurrency group, so site edits cannot replace a queued weekly coverage scan.

Acceptance:
- All registered sources and pending candidates are covered on a weekly cycle, in resumable batches.
- A persistent checkpoint records inventory hash, completed source IDs, results and remaining count.
- Normalized page-text hashes detect content changes.
- A previously accessible page becoming inaccessible, extraction becoming empty, or a previously visible vocal signal disappearing is flagged.
- A successful scan never implies opportunity completeness or publisher authenticity.

The next complete weekly cycle should compare hashes against this baseline and begin reporting actual changes and silent-miss indicators.

## P4 — Main-text and link extraction quality

**Status: three five-page comparisons completed (15 official source pages); structured link capture is now part of production collection.**

A separate evaluation workflow compared Scrapling, lxml full text and Trafilatura on identical official HTML snapshots. The corrected report separates:
- relevant anchor labels available in the DOM;
- labels retained in extracted text;
- exact href targets retained in Markdown;
- sitemap and feed discovery results.

Results show that parser text length alone is not an accuracy metric. Scrapling retained comparable relevant labels on the tested sources; lxml often included substantial page boilerplate; Trafilatura was weak on several list-heavy pages and remains evaluation-only. Carlo Felice was an exception where Trafilatura Markdown preserved more href targets than plain text, but a structured-link comparison is still needed before any production switch.

Production collection now preserves structured hrefs separately using lxml while keeping Scrapling for page fetching and text extraction. No discovered link is automatically promoted to an opportunity or application URL.

Acceptance:
- Compare title, dates, links, tables, role/voice type, eligibility, fees and application deadlines against manually reviewed evidence.
- Use parser-specific methods only where they improve completeness without losing structured details.
- Keep raw HTML snapshots and representative offline fixtures for repeatable tests.

## P5 — Evidence integrity and isolated PDF automation

**Status: PDF integrity baseline implemented; Docling pilot successful in isolation; signature verification and parser accuracy acceptance remain open.**

Current evidence:
- The isolated Docling 2.148.0 pilot converted 5/5 selected local PDF mirrors.
- All 5 SHA-256 values matched the integrity manifest.
- The sample covered 61 pages; all 61 pages had text provenance.
- Five tables were detected in one sample; no page was flagged as low-text.
- Combined conversion time was approximately 210 seconds.
- The sample included non-vocal controls and historical/administrative notices. “Basso” can mean an instrument such as “basso tuba”; the evaluator now reports voice_term_candidates separately from vocal_context and instrument_context.
- All extracted evidence remains pending_manual_review, is_verified=false and publication_eligible=false.
- The Docling workflow is isolated under experiments/pdf-parser and does not write to production opportunity data.
- No publisher digital signature has been verified.
- A read-only Poppler pdfsig audit is implemented and its first run inspected all eight local mirrors. Two PDFs contained signature fields: one had two signatures reported cryptographically valid but with unknown certificate issuers; another reported Digest Mismatch. The parser now distinguishes unsigned-PDF exit codes from tool errors and classifies Digest Mismatch as invalid; the corrected audit rerun is pending. Publisher identity remains not_verified until a trusted institution-to-certificate mapping exists.

Acceptance:
- Mirrored PDF files have a manifest with source record, local path, size, PDF-byte validation and SHA-256.
- SHA-256 is described only as byte-integrity evidence.
- Publisher signatures are marked verified only after cryptographic validation against a trusted publisher certificate/key.
- PDF extraction is isolated, page-grounded and tested against a manually annotated ground-truth set, including at least one confirmed scanned PDF and one current vocal recruitment PDF.
- Machine extraction remains pending manual review and cannot publish records.

## Completion policy

P0–P5 are engineering workstreams, not a claim that the whole platform is finished. P2 remains partial until the remaining sources have evidence-based strategies; P3 needs repeated weekly runs; P4 needs manual field-level precision/recall checks; P5 signature and parser acceptance require trusted signatures and representative ground-truth samples. Report these as pending until their evidence exists.
