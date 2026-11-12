---
name: official-source-verification
description: Verify Opera Lirico opportunities against primary organizer sources before publication.
---

# Official source verification

A discovery result is a lead, not a verified opportunity. Never publish from search snippets, social reposts, aggregators, cached summaries, or AI inference alone.

## Procedure
1. Open the organizer's own event page and identify the specific edition.
2. Locate the original announcement, regulations (bando), application form, or official calendar.
3. Record the canonical source URL and exact evidence passage supporting each important field.
4. Verify event title, organizer, teacher/cast, voice type or eligible applicants, location, event dates, application deadline, fees, required documents, and application URL independently.
5. Distinguish "not announced" from "free", "not open" from "closed", and an event date from its application deadline.
6. Record the checked time in Europe/Rome with an explicit UTC offset.
7. If key fields conflict across official documents, preserve both evidence records and leave the item pending manual review.

## Publication gate
Publish only when publisher_status=official, review_status=verified, publication_status=published, and non-empty primary-source evidence is attached. A successful HTTP response or keyword match is not evidence that an opportunity is valid.

## Output
Return a concise field-by-field verification summary, unresolved questions, exact official URLs, and a recommendation: verified, pending_manual_review, or rejected. Never silently fill missing values.
