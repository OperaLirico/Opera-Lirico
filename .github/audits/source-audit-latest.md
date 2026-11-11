# Daily source audit — 2026-11-11

- Audited today: **1 new source candidate**
- Auto-approved official: **0**
- Auto-approved third-party: **1**
- Needs review / duplicate / irrelevant / temporary unavailable / retired: **0 new classifications**
- Production source registry changes: **none**
- New candidate queue entries: **1** (discovery-only; not active in production scraping)

## Auto-approved third-party source

**Provinispettacolo — Musica**  
https://www.provinispettacolo.it/casting/musica/

- Publisher classification: third-party casting aggregator
- Automated review: `auto_approved_third_party`
- Confidence: high
- Relevance: relevant to singers and music opportunities
- Evidence: the category explicitly says it covers singers and music professionals; the site's submission page says notices are submitted by outside parties and warns that not all notices are in good faith.
- Decision: retain as a discovery-only third-party source. Do not treat its notices as official evidence.

Evidence pages:
- Music category: https://www.provinispettacolo.it/casting/musica/
- Publisher's submission and verification caveat: https://www.provinispettacolo.it/proponi-casting/
- Example opera-singer listing: https://www.provinispettacolo.it/audizioni-opera-lirica-roma-cantanti-professori-orchestra/

## High-priority opportunity lead — not published

The category currently links an Opera e Lirica audition listing that reports:
- Application deadline: **13 November 2026**
- Audition: **17 November 2026, 15:30–19:30**, Rome
- Voice types: soprano, mezzo-soprano, tenor, baritone and bass
- Preparation: two arias of the candidate's choice
- Application email shown by the third-party listing: candidatureopera@gmail.com
- Applicants are told to wait for written confirmation and an individual time slot.

No first-party organizer announcement was located in this audit. This remains a third-party lead only and was **not** added to `data/opportunities.json`. Do not present the dates, eligibility or application route as officially verified until the organizer's own evidence is found.

## Backlog and duplicate handling

- The 44-source baseline remains: 26 official, 4 third-party, 1 needs review, 13 irrelevant.
- The 15 `sources_extra.json` records are exact duplicates of entries already represented in the core source snapshot; they are not counted again.
- Existing `source-121` remains `needs_review` because its registered Robin Hood permalink is cross-genre. The stable Musica category is a separate candidate.
- No source was deleted, disabled, or promoted into the production fetch list.

## Coverage

The previous weekly scan completed **44/44** with no fetch failures. This new candidate was added after that inventory snapshot; the inventory is expected to contain 45 entries and requires a fresh coverage pass after merge.

## Files

- Candidate: `data/source_candidates.json` (`candidate-1`)
- Coverage logic: `audit_source_coverage.py`
- Policy: `docs/source-review-policy.md`
- Machine report: `.github/audits/source-audit-latest.json`
