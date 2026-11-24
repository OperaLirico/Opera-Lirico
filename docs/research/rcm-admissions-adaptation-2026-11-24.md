# OperaLab. Product Adaptation: Conservatoire Admissions and Audition Routes

- Date: 2026-11-24
- Reference study: ERA `docs/rea-research-lab/reports/2026-11-24-royal-college-of-music-desk-study.md`
- Reference site: https://www.rcm.ac.uk/
- Status: product specification only; no production implementation

## Product decision

OperaLab should represent conservatoire admissions as versioned, course-specific and route-specific requirements. A single generic “audition requirements” text field is not sufficient: repertoire, languages, media requirements, assessment stages and deadlines can vary by course, intake year and audition location/method.

The product should help Chinese-speaking applicants understand the official requirements without replacing or misrepresenting the institution's own instructions.

## 1. Data model principles

1. Every requirement belongs to a specific institution, course/programme and academic intake.
2. Audition route is a separate dimension: live, video, overseas pre-screening followed by live audition, portfolio or interview.
3. Assessment stages and their deadlines are separate records.
4. Preserve original official wording alongside OperaLab's Chinese explanation.
5. Never carry deadlines or requirements from a previous intake into a new one without verification.

## 2. Recommended logical entities

Map these concepts to the existing OperaLab schema before adding models:

- Institution
- Course / programme
- Academic intake / entry year
- Principal study / voice type
- Audition route
- Assessment stage
- Requirement item
- Deadline
- Official source and contact

### Audition route

Suggested fields:
- `audition_mode`: live / video / pre_screening_then_live / portfolio / interview
- `audition_location`: institution city / overseas city / online
- `route_eligibility`
- `stage_sequence[]`
- `route_deadlines[]`
- `source_url`
- `checked_at`

### Requirement item

Suggested fields:
- `requirement_type`: repertoire / language / recording / document / interview / technical / logistics / compliance
- `description_original`
- `chinese_explanation`
- `required_or_recommended`
- `course_scope`
- `route_scope`
- `intake_year`
- `source_url`

## 3. Student-facing page structure

1. Institution and course overview.
2. Intake year selector.
3. Eligibility and application requirements.
4. Audition repertoire checklist, grouped by language/genre/number of works.
5. Audition route selector and assessment-stage timeline.
6. Video submission checklist, only when relevant.
7. Interview and audition-day preparation.
8. Application, video and audition dates as separate milestones.
9. Official contacts, source links, last-checked date and verification state.

The original official text and OperaLab's explanatory translation must be visually distinguishable.

## 4. Critical data-quality rules

- Do not apply Masters requirements to undergraduate applicants unless explicitly stated.
- Do not assume all overseas audition venues use the same process.
- Do not assume a video audition is available for every course or principal study.
- Do not combine application deadline, video deadline and live audition date.
- Do not invent a file size, accepted format, repertoire requirement or language requirement.
- Mark unknown rules as “未确认” and link to the official admissions contact.
- Keep historical intake versions available for reference, but clearly label them as historical.

## 5. Minimum viable vertical slice

Implement one institution, one vocal course, one intake and one verified audition route before generalizing.

Acceptance tests:
- A different intake shows its own verified requirement version.
- Course-specific repertoire rules do not leak across degree levels.
- A pre-screening route renders video and live audition as separate stages.
- Video technical requirements appear only for the route that requires video.
- Each deadline is displayed as its own milestone.
- Official text and Chinese explanation are clearly distinguished.
- Every requirement has a source and checked date.
- Missing requirements remain unknown rather than copied from another course.

## 6. Implementation gates

Before coding, inspect current OperaLab institution/course schema, existing admissions records, routes, components and mobile layout. Reuse existing structures where possible and preserve current content.

Any implementation must use a separate branch, include data migration/backward compatibility checks if needed, test desktop and mobile, and remain unmerged/undeployed until explicitly approved.

No production code or data is changed by this specification.
