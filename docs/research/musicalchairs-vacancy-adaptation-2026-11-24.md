# OperaLab. Product Adaptation: Professional Vacancy and Audition Brief

- Date: 2026-11-24
- Reference study: ERA `docs/rea-research-lab/reports/2026-11-24-musicalchairs-desk-study.md`
- Reference site: https://www.musicalchairs.info/
- Status: product specification only; no production implementation

## Product decision

OperaLab should distinguish professional employment and audition vacancies from courses, degree admissions, competitions and masterclasses. A vacancy detail should function as a practical audition brief, not just a title, organization and deadline.

Absorb the structured vacancy and employer-publishing concepts; do not copy Musicalchairs' branding, listing text, paid rates, or data.

## 1. Opportunity type and voice taxonomy

Keep opportunity types explicit:

- opera_company_audition
- chorus
- orchestra
- teaching
- degree_course
- course
- competition
- masterclass
- grant
- festival_or_project
- other

Keep voice types granular in the data model (soprano, mezzo-soprano, contralto, countertenor, tenor, baritone, bass, etc.). The UI may group categories for navigation, but a grouped label such as “Soprano / Mezzo” must not destroy the underlying distinction.

## 2. Vacancy detail: separate the stages

A professional vacancy should distinguish:

### Application stage
- CV and biography
- headshot / full-body photo
- audio or video recording
- proposed repertoire
- references or other documents
- application method and destination

### Audition stage
- audition date(s) and location(s)
- repertoire to prepare
- sight-reading / a vista requirement
- pianist provided or not
- accompaniment or score requirements
- interview or additional rounds

A submitted recording is not necessarily the same as live audition repertoire. Do not combine both into one generic “repertoire” field.

## 3. Recommended normalized fields

Only map or add fields after inspecting the existing schema and records.

| Field | Purpose |
|---|---|
| `opportunity_type` | job / chorus / teaching / degree / course / competition etc. |
| `position_title` | Exact advertised position |
| `employer_id` | Organization reference |
| `contract_type` | Full-time / part-time / fixed-term / freelance / extra / substitute / unknown |
| `paid_status` | Paid / unpaid / tuition-based / stipend / unknown |
| `compensation_details` | Original published terms; do not infer |
| `voice_types[]` | Granular voice-type eligibility |
| `application_materials[]` | CV, photo, audio, video, repertoire list, references |
| `application_deadline` | Application closing date |
| `application_method` | Email / official form / external portal / other |
| `audition_dates[]` | One or more published audition dates |
| `audition_location` | Venue, city, country or online |
| `audition_repertoire[]` | Required live audition repertoire |
| `sight_reading_required` | Explicitly stated sight-reading requirement |
| `pianist_provided` | Explicitly stated accompaniment availability |
| `recording_consent` | Only if a notice explicitly states it |
| `official_source_url` | Official vacancy or organizer page |
| `source_checked_at` | Last verification timestamp |
| `verification_status` | Verified / needs review / expired / inaccessible |

Preserve the original wording and language for important requirements. Keep normalized values for search, with the original source text available for verification.

## 4. Opportunity detail page order

1. Position title, employer, location and opportunity type.
2. Contract type and compensation status.
3. Eligible voice type, role and candidate requirements.
4. Application materials.
5. Audition repertoire and process.
6. Dates, venue and practical logistics.
7. Closing date and application method.
8. Official source, verification state and last checked date.

Use clear labels for “application deadline” versus “audition date”. Do not display a job as paid unless compensation is explicitly supported by the source.

## 5. Search and navigation

- Filter by opportunity type, granular voice type, country/city, contract type, paid status and closing-date range.
- Show the difference between “professional vacancy” and “training/course”.
- Support broad grouped voice navigation while retaining precise voice filters.
- Surface latest listings only when publication date and source-check date are both available.
- Make current/past/all scope explicit.

## 6. Future organizer publishing workflow

A later organizer portal may allow:
- verified organization profile;
- structured listing submission;
- mandatory official source and deadline;
- required opportunity type and eligibility fields;
- moderation and evidence review;
- listing expiry and periodic reconfirmation;
- change history.

Do not publish unverified submissions as verified opportunities. Paid promotion, if ever introduced, must be visibly distinguished from organic ranking and must not affect trust status.

## 7. Minimum viable vertical slice and acceptance tests

Before coding, inspect current OperaLab schema, existing opportunity records, page routes and component ownership.

A first vertical slice should cover one professional vacancy list/detail route.

Acceptance tests:
- A chorus vacancy with CV, photo, recording and repertoire requirements displays each separately.
- A vacancy with multiple audition dates displays every date separately from its application deadline.
- A listing with unknown compensation shows “not specified”, never inferred paid status.
- Soprano and mezzo can be searched independently even if a navigation group combines them.
- A course cannot appear as a salaried vacancy without explicit type and compensation evidence.
- Every vacancy detail links to its official source and shows last checked date.
- Mobile layout preserves the application deadline, audition dates and apply action without horizontal overflow.

## 8. Implementation gates and non-goals

- No schema or UI changes until current data structures are reviewed.
- Reuse existing models and components; avoid duplicate taxonomies.
- Keep all work on a separate branch with backward compatibility and rollback plan.
- No production merge or deployment without explicit approval.
- Do not bypass reference-site anti-bot controls.
- Do not copy listing text or imply a third-party job is still open without rechecking the official source.
- Do not introduce a paid organizer portal before trust and moderation workflows exist.
