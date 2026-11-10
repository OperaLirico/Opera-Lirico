# Source audit baseline — 2026-11-10

## Scope and baseline

- Repository baseline: `main` at `42ba2a354c90a3bc5bae994a4db2593f263c7eac`
- Core registry: **44** records in `data/sources.json`
- Extra registry: **15** records in `data/sources_extra.json`
- Exact cross-file duplicates: **15/15** extra records match a core record by legacy number and URL.
- Unique sources audited in this baseline: **44**.

The duplicate finding is a data-quality flag only. No records were deleted, merged, disabled, or removed from a production registry.

## Classification

| Classification | Count | Meaning |
|---|---:|---|
| `auto_approved_official` | 23 | First-party source for its own institution or event, with relevant vocal content evidenced |
| `auto_approved_third_party` | 4 | Useful third-party aggregator; individual notices must be traced back to organizers |
| `needs_review` | 5 | Publisher may be identifiable, but relevance, maintenance value, or identity evidence is incomplete |
| `irrelevant_candidate` | 12 | The inspected notice is actor-only, instrument-only, generic project submission, or unrelated hiring |

## Main findings

1. The 15 records in `sources_extra.json` are exact duplicates of records already present in `sources.json`. Keep both files untouched until the registry architecture is reviewed; duplication is recorded as metadata.
2. The registry contains several clearly out-of-scope items: actor-only auditions, instrument-only orchestra jobs, generic theatre project calls, and non-artistic vacancies.
3. Some official institution pages are mixed-purpose. Their publisher identity can be trusted while individual notices still need vocal-role filtering.
4. Third-party aggregators such as Sportello Spettacolo, Opera Mundus, and Liricamente can provide discovery value, but should never replace the original organizer notice as the final evidence for dates, eligibility, fees, or application links.
5. The review queue prioritizes uncertain source relevance or identity, remaining priorities include AsLiCo, Teatro Lirico di Cagliari, Musical.it, and cross-genre casting notices. Follow-up evidence has now confirmed Maggio Musicale Fiorentino, Teatro Lirico Sperimentale di Spoleto, and Fondazione Renata Tebaldi as official vocal sources; Winterwerft is out of scope for the classical-vocal registry.

## Important limitations

- This is a source-level baseline, not an audit of every individual opportunity.
- An HTTP 200 response only indicates page accessibility; it does not prove official identity, relevance, or current application status.
- “Official” means first-party for the publisher's own institution or event. It does not imply government endorsement or independent accreditation.
- Search and page evidence was gathered for this baseline; sources without adequate direct evidence remain `needs_review`.
- PR #4 candidate discoveries are not part of the `main` baseline and must be audited separately after inspecting that branch.
- No production workflow, source activation flag, public opportunity data, or live website content was changed.

## Files

- Machine-readable audit: [`reports/source-audit-baseline-2026-11-10.json`](./source-audit-baseline-2026-11-10.json)


## Follow-up verification (2026-11-10)

- **Maggio Musicale Fiorentino**: confirmed official and relevant. Its official Bandi page lists vocal academy programmes; the 2026/27 Ensemble Corale notice specifies bass, baritone and tenor auditions. See [Bandi](https://www.maggiofiorentino.com/bandi/) and [Ensemble Corale notice](https://www.maggiofiorentino.com/bandi/bando-ensemble-corale).
- **Teatro Lirico Sperimentale di Spoleto “A. Belli”**: confirmed official and relevant. The institution's history describes its young opera-singer competition and training mission; its official 2026 free auditions were for opera singers. See [institution history](https://www.tls-belli.it/storia/) and [2026 auditions](https://www.tls-belli.it/2026/03/06/libere-audizioni-2026/).
- **Fondazione Renata Tebaldi**: confirmed official and relevant. Its foundation profile and 2026 competition notice establish a biennial international voice competition for opera singers. See [foundation](https://www.fondazionerenatatebaldi.org/) and [2026 competition notice](https://www.fondazionerenatatebaldi.org/bando-2026-2/).
- **Winterwerft**: marked irrelevant for this registry. The open call sought multidisciplinary theatre/performance projects and music groups, not individual classical singers; its deadline was 8 November 2026.
- **AsLiCo**: remains `needs_review` until a direct official programme page and current voice-specific admissions evidence can be confirmed.
