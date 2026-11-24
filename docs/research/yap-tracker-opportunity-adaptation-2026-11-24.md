# OperaLab. Product Adaptation: Opportunity Discovery and Tracking

- Date: 2026-11-24
- Reference study: ERA `docs/rea-research-lab/reports/2026-11-24-yap-tracker-desk-study.md`
- Reference site: https://www.yaptracker.com/
- Status: product specification only; no production implementation

## Product decision

OperaLab. should absorb the useful workflow patterns behind YAP Tracker while keeping its own positioning: a Chinese-language, source-transparent European vocal-arts information and learning platform. Do not copy its branding, wording, member-only catalogue, or private user data.

The product should evolve from a collection of opportunity cards into a trustworthy opportunity lifecycle:

`Discover → Assess → Save → Prepare → Apply → Audition → Outcome → Archive`

The public information layer and each user's private tracking layer must remain separate.

## 1. Opportunity taxonomy

Use explicit, non-overlapping opportunity types where possible:

- Opera-house / company auditions and chorus calls
- Young Artist Programmes
- Resident Artist / Opera Studio programmes
- Vocal competitions
- Masterclasses and workshops
- Conservatory degree admissions
- Festivals and performance projects
- Scholarships and grants
- Mainstage / soloist / concert opportunities

Keep conservatory degree admissions distinct from professional training or opera-company programmes. A pay-to-sing course must not be labelled as a salaried young artist programme.

## 2. Multi-route deadlines (important data-model requirement)

A programme may have several audition cities and a separate recording deadline. Do not force all dates into a single `deadline` field.

Recommended child object: `application_routes[]`

| Field | Purpose |
|---|---|
| `route_type` | in_person / recording / online / application_only |
| `location` | city, country, venue or virtual |
| `deadline_at` | normalized date/time when explicitly published |
| `deadline_timezone` | timezone if known |
| `deadline_label_original` | exact original wording, e.g. “Received by” |
| `audition_date_or_range` | published audition date/range |
| `application_url` | route-specific application link |
| `requirements_override` | route-specific instructions |
| `source_url` | direct supporting official source |

Preserve the original deadline phrase. Do not convert a date-only deadline into a guessed time or timezone.

## 3. Opportunity detail requirements

Every detail page should make these items easy to scan:

1. Organizer and programme/season.
2. Opportunity type and eligible voice types/roles.
3. Age, nationality/residency, career-stage and other eligibility requirements.
4. Repertoire, recording and document requirements.
5. Fees, tuition, salary, stipend and scholarships as separate concepts.
6. All audition/application routes and their individual deadlines.
7. Official application link and whether it is external.
8. Source authority, last-checked date and verification state.

Unknown values must display as “未公布 / 未确认”, never be inferred.

## 4. Search and filter behavior

Initial filters should prioritize the decisions singers actually make:

- opportunity type;
- voice type;
- country/city and online/recording format;
- deadline range;
- career stage / age eligibility;
- paid / unpaid / tuition / scholarship / unknown.

Keep “current / past / all” visible. Show active filters and provide a clear reset. Do not silently hide records because of a default personal status such as “undecided”.

## 5. Personal tracking — later phase

After confirming account and privacy architecture, add private user states:

`saved → interested → preparing → applied → audition_invited → auditioned → offered/rejected/withdrawn → archived`

Potential later additions:
- deadline reminders and calendar export;
- personal notes and preparation checklist;
- optional expense tracking.

Personal notes, application status, uploaded materials and audition outcomes must never be exposed as public opportunity facts or to other users. Do not reproduce peer outcome alerts from other platforms.

## 6. Minimum viable vertical slice

Before a large redesign, implement one narrow end-to-end flow:

- Opportunity list with type, voice and location filters.
- Detail page with source, verification state and route-specific deadlines.
- At least one existing verified record with multiple application routes, if such a record exists in the current dataset.
- External application link clearly labelled.
- Mobile layout with filters discoverable and deadline information readable.

### Acceptance tests

- A programme with three in-person audition cities and one recording deadline renders four separate routes.
- Filtering by voice and country uses verified fields only.
- Current/past/all scope is visible and does not hide results unexpectedly.
- Missing fee, age or deadline fields display as unknown.
- External application actions are labelled as external.
- Every deadline row links to the source that supports it.

## 7. Implementation gates

Before coding, inspect the existing OperaLab schema, data files, route structure and CSS ownership. Reuse existing fields and components where safe; do not add duplicate models or a new backend solely for this feature.

Any implementation must:
- be on a separate branch;
- include schema migration/backward-compatibility checks if needed;
- preserve all existing records;
- include list/detail and mobile QA;
- have a rollback path;
- remain unmerged and undeployed until explicitly approved.

## 8. Explicit non-goals

- Do not reproduce YAP Tracker's paywall or paid membership strategy.
- Do not scrape member-only content or bypass access controls.
- Do not store sensitive application documents in the first iteration.
- Do not infer or publish unverified eligibility, costs, deadlines or outcomes.
- Do not start a full-site rewrite based on this single reference study.
