# Daily source audit — 2026-11-11

- Audited today: **2 new source candidates**
- Auto-approved official: **1**
- Auto-approved third-party: **1**
- New needs-review / duplicate / irrelevant / temporary unavailable / retired classifications: **0**
- Production source registry changes: **none**
- New candidate queue entries: **2**; both remain outside production activation.

## Auto-approved official source

**Teatro Lirico Sperimentale di Spoleto — 81st International Singing Competition**  
https://www.tls-belli.it/concorso-di-canto-2026/

- Classification: `auto_approved_official`; confidence high.
- Direct official evidence: the institution's [Bandi e avvisi page](https://www.tls-belli.it/bandi_e_avvisi/) links directly to the competition page; the page identifies a competition for young opera singers and its footer names Istituzione Teatro Lirico Sperimentale di Spoleto “A. Belli”.
- Visible page information: Spoleto, Teatro Caio Melisso, **16–20 February 2027**; the page says the bando and details will be available soon.
- **Important internal conflict:** the crawler's HTML title metadata says “80° Concorso Internazionale di Canto”, while the visible page body says “81ª edizione”. The edition number remains unresolved until the official bando appears.
- No application deadline, eligibility, fee, application route or official PDF is available. This is a source registration, **not an opportunity record**.
- The separate [Libere Audizioni 2026 page](https://www.tls-belli.it/libere-audizioni-2026/) has a 20 March 2026 deadline and is historical.
- robots.txt for this exact child path could not be independently retrieved. The parent page is already an existing source and was fetched successfully, and the new page returned HTTP 200 in coverage; nevertheless, the new child page remains inactive pending the access-policy check.

## Auto-approved third-party source

**Provinispettacolo — Musica**  
https://www.provinispettacolo.it/casting/musica/

- Publisher classification: third-party casting aggregator; `auto_approved_third_party`, high confidence.
- The category explicitly covers singers and music professionals. Its [submission policy](https://www.provinispettacolo.it/proponi-casting/) says notices are submitted by outside parties and warns that not all notices are in good faith.
- Retain as a discovery-only third-party source. Individual opportunities must be checked against the organizer; no notice from this source is official evidence by itself.

## High-priority third-party opportunity lead — not published

The [Opera e Lirica audition listing](https://www.provinispettacolo.it/audizioni-opera-lirica-roma-cantanti-professori-orchestra/) reports:

- Application deadline: **13 November 2026** (no time stated on this listing).
- Audition: **17 November 2026, 15:30–19:30**, St. Paul's Within the Walls Church, Rome.
- Voice types: soprano, mezzo-soprano, tenor, baritone and bass; two arias of the candidate's choice.
- Contact shown by the listing: candidatureopera@gmail.com; written confirmation and an individual time slot are required.

The [official Opera e Lirica website's separate job page](https://www.opera-lirica.com/it/content/11-lavora-con-noi) also lists the same email, corroborating that the address is used by the organization. It does **not** publish this specific singer audition. Another third-party listing reports a 13 November 19:00 deadline, but that time is not adopted without an official notice.

**No first-party announcement for this specific audition was located.** Its dates, requirements and application route remain third-party-only and were not added to `data/opportunities.json`.

## Existing review backlog and duplicate handling

- Registered baseline: 44 sources — 26 official, 4 third-party, 1 needs review, 13 irrelevant.
- The 15 `sources_extra.json` records are exact duplicates already represented in the core source snapshot; they are not counted again.
- `source-121` remains `needs_review`. Its Robin Hood page names tenor, soprano, baritone and bass roles, but is a low-budget mixed musical-theatre production requiring acting and singing, not a clear core classical-opera source. It was not deleted, disabled or promoted.
- No existing production source was deleted, disabled or changed.

## Latest full coverage and monitoring follow-up

- The post-merge weekly coverage scan completed **46/46**: 44 registered sources + 2 candidates; **0 failures, 0 restricted pages, 0 extraction errors, 0 anomalies**.
- Both candidates returned HTTP 200. Candidate-1 and candidate-2 are included in the completed inventory.
- The earlier 45-item pass had a 25-second timeout for source-10 and HTTP 202 empty extractions for source-115, source-117 and source-120. The subsequent 46-item pass rechecked all four successfully (HTTP 200, no anomalies). Their existing relevance classifications were not changed.
- Candidate-2's access policy for the child path remains unverified; a successful HTTP response does not replace the robots/terms check. It remains a pending source candidate and is not production-activated.
- Inventory SHA-256: `3830ac0c9ca41cf14b119aaf2376dfd86c357fc05588afd3ab2d1aa1acc17cd8` (inventory identity only; not source authentication or publisher signature).

## Files and next check

- Candidate queue: `data/source_candidates.json` (`candidate-1`, `candidate-2`)
- Machine report: `.github/audits/source-audit-latest.json`
- Weekly checkpoint: `.github/audits/source-coverage-checkpoint.json`
- Weekly coverage is complete for the current 46-item inventory; no further full scan is needed today.
