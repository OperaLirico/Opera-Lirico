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
| `auto_approved_official` | 26 | First-party source for its own institution or event, with relevant vocal content evidenced |
| `auto_approved_third_party` | 4 | Useful third-party aggregator; individual notices must be traced back to organizers |
| `needs_review` | 1 | Publisher may be identifiable, but relevance, maintenance value, or identity evidence is incomplete |
| `irrelevant_candidate` | 13 | The inspected notice is actor-only, instrument-only, generic project submission, or unrelated hiring |

## Main findings

1. The 15 records in `sources_extra.json` are exact duplicates of records already present in `sources.json`. Keep both files untouched until the registry architecture is reviewed; duplication is recorded as metadata.
2. The registry contains several clearly out-of-scope items: actor-only auditions, instrument-only orchestra jobs, generic theatre project calls, and non-artistic vacancies.
3. Some official institution pages are mixed-purpose. Their publisher identity can be trusted while individual notices still need vocal-role filtering.
4. Third-party aggregators such as Sportello Spettacolo, Opera Mundus, and Liricamente can provide discovery value, but should never replace the original organizer notice as the final evidence for dates, eligibility, fees, or application links.
5. The remaining manual review priority is the Provinispettacolo record: the domain has useful opera-audition notices, but the currently registered permalink is a cross-genre Robin Hood casting notice rather than a primary organizer page. Musical.it has been marked out of scope for the current classical-vocal registry.

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
- **AsLiCo**: confirmed official and relevant. Its own site describes its mission to select young opera singers and provide training and stage-debut opportunities; its current competition pages include the 78th Young Opera Singers competition. See [AsLiCo](https://aslico.org/), [Who we are](https://aslico.org/aslico/), and [current edition](https://aslico.org/edizione-in-corso/).


- **Teatro Verdi Trieste**: upgraded to `auto_approved_official`. Its official 2026 recruitment page contains closed choir selections for mezzosoprano/contralto and tenore/baritono, with official notices, application forms, repertoire and results. The page also lists orchestra positions, so individual notices must still be filtered by role. [Official 2026 notices](https://www.teatroverdi-trieste.com/amministrazione-tras/bandi-di-concorso-2026/).
- **Teatro Lirico di Cagliari**: upgraded to `auto_approved_official`. Its official notice dated 6 November 2026 opens an international selection for 2027 choir artists and links the public notice, application form, exam schedule and repertoire. [Official 2027 choir selection](https://www.liricocagliari.it/bandi-e-gare/approvazione-avviso-pubblico-e-indizione-selezione-internazionale-per-esami-volta-alla-costituzione-di-una-graduatoria-di-idonei-valevole-in-aggiunta-alle-vigenti-graduatorie-dei-titolari-di-diritt/).
- **Musical.it**: classified `irrelevant_candidate` for this registry's current scope. Its audition board is oriented toward musical-theatre performers, dancers, acrobats and musical-theatre training. It may be useful only if a separate musical-theatre category is introduced. [Audition board](https://www.musical.it/audizioni).
- **Provinispettacolo**: retained as `needs_review`, not auto-approved. The site has published an Opera e Lirica call for classical voice types, but the registered Robin Hood permalink is a cross-genre casting notice. Future handling should register a stable category/listing page separately from individual notices and trace each opportunity to its organizer. [Opera e Lirica listing](https://www.provinispettacolo.it/audizioni-opera-lirica-roma-cantanti-professori-orchestra/) and [site homepage](https://www.provinispettacolo.it/).

Corrected item-level classification totals: **26 official, 4 third-party, 1 needs review, 13 irrelevant** (44 unique sources). The earlier summary count of 2 needs-review and 12 irrelevant was a reporting arithmetic error; the per-item labels themselves were unchanged. No source registry or production activation flag was modified.
