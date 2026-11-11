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

- Classification: `auto_approved_official`
- Confidence: high
- Direct official evidence: the institution's official [Bandi e avvisi page](https://www.tls-belli.it/bandi_e_avvisi/) links directly to the competition page; the competition page identifies the 81st edition for young opera singers and the footer names Istituzione Teatro Lirico Sperimentale di Spoleto “A. Belli”.
- Published information: Spoleto, Teatro Caio Melisso, **16–20 February 2027**.
- Current limitation: the page says the bando and detailed information will be available soon. No application deadline, eligibility, fee, application route or official PDF is available yet.
- Decision: high-confidence official source candidate; `review_status=pending_manual_review`, `production_activation=false`. This is a source registration, **not an opportunity record**.
- The separate [Libere Audizioni 2026 page](https://www.tls-belli.it/libere-audizioni-2026/) gives a 20 March 2026 deadline and is historical; it was not treated as a current opportunity.
- robots.txt for this exact child path could not be independently retrieved in this audit. The parent page is already an existing source and was fetched successfully by the current Daily source refresh; nevertheless, the new child page remains inactive pending the access-policy check.

## Auto-approved third-party source

**Provinispettacolo — Musica**  
https://www.provinispettacolo.it/casting/musica/

- Publisher classification: third-party casting aggregator.
- Automated review: `auto_approved_third_party`; confidence high.
- The category explicitly covers singers and music professionals. Its [submission policy](https://www.provinispettacolo.it/proponi-casting/) says notices are submitted by outside parties and warns that not all notices are in good faith.
- Decision: retain as a discovery-only third-party source. Individual opportunities must be verified against the organizer; no notice from this source is official evidence by itself.

## High-priority third-party opportunity lead — not published

The [Opera e Lirica audition listing](https://www.provinispettacolo.it/audizioni-opera-lirica-roma-cantanti-professori-orchestra/) reports:

- Application deadline: **13 November 2026** (no time stated on this listing).
- Audition: **17 November 2026, 15:30–19:30**, St. Paul's Within the Walls Church, Rome.
- Voice types: soprano, mezzo-soprano, tenor, baritone and bass.
- Preparation: two arias of the candidate's choice.
- Contact shown by the listing: candidatureopera@gmail.com; written confirmation and an individual time slot are required.

Cross-check: the [official Opera e Lirica website's separate job page](https://www.opera-lirica.com/it/content/11-lavora-con-noi) also lists candidatureopera@gmail.com, corroborating that the address is used by the organization. It does **not** publish this specific singer audition. Another third-party listing reports a 13 November 19:00 deadline, but that time is not adopted because it is not confirmed by an official notice.

**No first-party announcement for this specific audition was located.** Its dates, requirements and application route remain third-party-only and were not added to `data/opportunities.json`.

## Existing review backlog and duplicate handling

- Registered baseline: 44 sources — 26 official, 4 third-party, 1 needs review, 13 irrelevant.
- The 15 `sources_extra.json` records are exact duplicates already represented in the core source snapshot; they are not counted again.
- `source-121` remains `needs_review`. Its Robin Hood page names tenor, soprano, baritone and bass roles, but is a low-budget mixed musical-theatre production requiring acting and singing, not a clear core classical-opera source. It was not deleted, disabled or promoted.
- No existing production source was deleted, disabled or changed.

## Monitoring exceptions from the weekly coverage scan

- Coverage completed **45/45** with 0 remaining. The new TLS competition page was discovered after that scan and requires the next inventory pass (expected 46 entries).
- `source-10` had one 25-second Scrapling timeout in the weekly batch. The existing Daily source refresh fetched its parent page successfully at **2026-11-11 11:09:07 Europe/Rome (HTTP 200)**, and manual page inspection also succeeded. Treat as intermittent; keep active and retry on the normal cycle.
- `source-115` (Fondazione Aida), `source-117` (Attoricasting) and `source-120` (Orchestra della Toscana) returned HTTP 202 with empty extraction. Manual inspection confirmed actress/technical/promotional roles, actor/actress comedy casting, and a Primo Oboe-only competition respectively. Their existing `irrelevant_candidate` classifications remain unchanged.
- No 403/429 or login/CAPTCHA restriction was recorded in this scan.

## Files and next check

- Candidate queue: `data/source_candidates.json` (`candidate-1`, `candidate-2`)
- Machine report: `.github/audits/source-audit-latest.json`
- The next coverage run should include candidate-2; no production fetch method or source activation was changed.
