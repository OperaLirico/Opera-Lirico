# Opportunity data and publication policy

## One record per opportunity

Current, individual auditions, choir selections, competitions and young-artist programmes belong in `data/opportunities.json`. Do not treat a source page as if it were one opportunity: a theatre page may contain several separate notices with different voice types, deadlines and audition dates.

## Publication gate

A record is eligible for public display only when all three conditions are true:

- `publication_status = published`
- `review_status = verified`
- `publisher_status = official`

The frontend also hides records without a parseable application deadline and records whose application deadline has passed. Expired opportunities must not be represented as currently open.

## Evidence and dates

- `source_url`: stable page belonging to the institution or event.
- `announcement_url`: the actual first-party notice/listing page.
- `application_url`: direct application form, when known and verified.
- `official_pdf_url`: the organizer's original PDF, when available.
- `evidence`: short source excerpts, URLs, check timestamps and PDF page numbers where applicable.
- `application_deadline_at`, `audition_start_at`, `audition_end_at`, and performance dates are separate. Never substitute an audition date for an application deadline.
- All date-time values must include an explicit timezone. For Italian local dates, use the correct Europe/Rome offset for that date.

## Review and maintenance

- Discovery results remain drafts until the organizer, vocal relevance, dates, eligibility and links are checked.
- Third-party listings may be used to discover a notice, but do not qualify as first-party evidence for a published record.
- A single notice containing different voice types with different audition times should be split into separate records.
- Unknown dates, fees, age limits and eligibility conditions must be omitted or explicitly described as unknown; never infer them.
- Preserve old records for auditability. Archive or update expired records rather than silently deleting them.
