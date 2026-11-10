# Source review and opportunity data policy

## Source discovery is not source approval

New URLs discovered by automation are written to `data/source_candidates.json`.
Every new item starts with:

- `review_status: pending_manual_review`
- `screening_status: heuristic_passed`
- `publisher_status: unverified`

Passing keyword and vocal-relevance checks only means the candidate is worth a human look. It does not prove that the publisher is official, that the page is a durable source, or that an opportunity is open.

The existing `data/sources_extra.json` entries were admitted by earlier keyword heuristics. They are retained for continuity and tagged `legacy_unreviewed`; do not treat that tag as verified approval.

## Manual source approval

Before changing a candidate to an approved source, verify:

1. The page belongs to the named institution or is an explicitly trusted specialist listing.
2. The page regularly publishes vocal/opera-related opportunities, not unrelated staff or instrumental vacancies.
3. The URL is a stable listing or official announcement page, not a social-share link or a temporary application form.
4. The page's purpose and target applicants are clear.
5. The source's canonical URL and evidence are recorded.

Rejected candidates remain auditable; do not silently erase them.

## Opportunity records

Use `data/opportunity.schema.json` for structured opportunity records. Keep these dates separate:

- application opening and deadline;
- audition start and end;
- performance start and end.

Do not infer missing dates, age limits, fees, voice types, or eligibility. Use source excerpts and evidence URLs. Unknown means absent or explicitly unknown, never guessed.

A record may be publicly displayed only when both conditions hold:

- `review_status = verified`
- `publication_status = published`

For publication, the publisher must also be confirmed official. Third-party listings may be retained as leads but must link to the original organizer announcement before publication.

## Snapshot retention

For a known source, a failed fetch must not replace the last successful extract with an empty page. Keep the previous content and record the failed attempt separately with:

- `last_attempt_at`
- `last_attempt_status`
- `last_attempt_http_status` / `last_attempt_error`
- `consecutive_failures`
- `stale = true`

A successful refresh replaces the snapshot, updates `last_success_at`, clears the failure count, and sets `stale = false`. A stale snapshot is historical evidence, not proof that its opportunities remain open.
