# Initial data-quality audit

Date: 2026-11-10
Scope: read-only spot check of `data/sources.json`, `data/sources_extra.json`, and `data/conservatori.json` on `feature/repo-foundation`.

This is a preliminary sample review, not a complete audit of every record. No production data or website files were changed.

## Findings

### 1. HTTP success is not the same as a valid, open opportunity

Several source records have `status: "ok"` because the source page responded successfully, while the visible evidence includes past deadlines. Examples in the current snapshot include:
- Teatro alla Scala: the listed choir audition closed on 15 May 2026.
- Teatro Carlo Felice: one listed application deadline was 23 October 2026.
- Fondazione Luciano Pavarotti: a notice says applications closed on 28 October 2026.

The UI and data model should keep source-fetch health separate from opportunity lifecycle state (open, closed, upcoming, unknown).

### 2. Broad discovery can introduce opportunities outside the target audience

The sampled `sources_extra.json` includes general theatre and arts jobs, technical roles, and instrumental orchestra vacancies (for example, an oboe competition). These may be valid cultural-sector notices, but they are not necessarily useful to classical singers.

Add an explicit audience/category classification before displaying discovered items in the singer-focused opportunity feed.

### 3. Conservatory pages can contain mixed academic years and stale documents

The sampled `conservatori.json` records contain current 2026/2027 pages alongside documents from earlier years (including 2015 programme PDFs). A page being reachable does not mean every linked document is current or relevant to vocal admissions.

Each document should carry its own academic year, instrument/discipline, source URL, and last-checked date where these can be established.

### 4. Some key facts are not yet normalized

The current records mostly preserve snippets such as deadline lines and exam-date lines. These are useful evidence, but they are not consistently normalized into structured fields such as:
- application deadline (ISO date and time, with timezone where stated)
- opportunity or academic year
- voice type / discipline
- eligibility and age limits
- application materials
- official application URL
- last verified date and reviewer status

Do not infer missing facts from unrelated lines on the same page.

## Recommended next steps

1. Introduce a review status separate from fetch status: `pending_review`, `verified_open`, `verified_closed`, `needs_update`.
2. Add opportunity categories and a singer-relevance check before items enter the public singer feed.
3. Normalize dates only when the source wording supports an unambiguous date; otherwise retain the evidence snippet and mark the date unknown.
4. Keep the original official URL and the exact evidence lines used for each displayed fact.
5. Build a small review queue first. Do not automatically publish Docling-extracted values.

## Safety / scope

This document is an audit note only. It does not change `main`, the public Pages site, the existing daily workflow, or production JSON files.
