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
| `auto_approved_official` | 20 | First-party source for its own institution or event, with relevant vocal content evidenced |
| `auto_approved_third_party` | 4 | Useful third-party aggregator; individual notices must be traced back to organizers |
| `needs_review` | 9 | Publisher may be identifiable, but relevance, maintenance value, or identity evidence is incomplete |
| `irrelevant_candidate` | 11 | The inspected notice is actor-only, instrument-only, generic project submission, or unrelated hiring |

## Main findings

1. The 15 records in `sources_extra.json` are exact duplicates of records already present in `sources.json`. Keep both files untouched until the registry architecture is reviewed; duplication is recorded as metadata.
2. The registry contains several clearly out-of-scope items: actor-only auditions, instrument-only orchestra jobs, generic theatre project calls, and non-artistic vacancies.
3. Some official institution pages are mixed-purpose. Their publisher identity can be trusted while individual notices still need vocal-role filtering.
4. Third-party aggregators such as Sportello Spettacolo, Opera Mundus, and Liricamente can provide discovery value, but should never replace the original organizer notice as the final evidence for dates, eligibility, fees, or application links.
5. The review queue prioritizes uncertain source relevance or identity, including Maggio Musicale Fiorentino, AsLiCo, Teatro Lirico di Spoleto, Fondazione Renata Tebaldi, Winterwerft, Musical.it, and cross-genre casting notices.

## Important limitations

- This is a source-level baseline, not an audit of every individual opportunity.
- An HTTP 200 response only indicates page accessibility; it does not prove official identity, relevance, or current application status.
- “Official” means first-party for the publisher's own institution or event. It does not imply government endorsement or independent accreditation.
- Search and page evidence was gathered for this baseline; sources without adequate direct evidence remain `needs_review`.
- PR #4 candidate discoveries are not part of the `main` baseline and must be audited separately after inspecting that branch.
- No production workflow, source activation flag, public opportunity data, or live website content was changed.

## Files

- Machine-readable audit: [`reports/source-audit-baseline-2026-11-10.json`](./source-audit-baseline-2026-11-10.json)
