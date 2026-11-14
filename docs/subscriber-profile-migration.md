# Subscriber and profile migration plan

## Goals

Keep the existing Opera Lirico newsletter working while introducing optional singer profiles for personalized opportunity matching. Existing subscribers must not be forced to register again, lose their subscription, or have a profile silently inferred from their email address.

## Current systems

- Buttondown remains the newsletter subscription and email-delivery system.
- The current private Cloudflare Worker KV binding `CONTENT_DRAFTS` is only for social-content review drafts. It must not be reused for subscriber profiles.
- The matching engine in `content_engine/matcher.py` is a pure function. It does not read subscriber records, persist profiles, or send email.

## Subscriber groups

### Existing newsletter subscribers

- Preserve every existing Buttondown subscriber and their current subscription state.
- Do not bulk-copy subscriber emails into a new profile database.
- Do not require existing subscribers to complete a profile.
- If a profile-completion invitation is sent in the future, first verify that the original subscription/consent and applicable legal basis permit that communication.
- The invitation should link to a secure, email-verified profile-completion flow. The user chooses whether to provide additional details.
- A subscriber who ignores the invitation continues receiving the ordinary newsletter according to their existing subscription status.

### New subscribers

- Keep newsletter opt-in explicit and separate from optional personalized-recommendation consent.
- New subscribers may subscribe with email only. Profile completion is optional.
- Do not activate profile matching unless the user has provided the required profile fields and the relevant consent.

## Proposed profile fields

| Field | Requirement | Notes |
|---|---|---|
| Email | Required for verified account linking | Normalize for matching; never expose publicly |
| Name | Optional | Display/personalization only |
| Voice type | Required for matching | soprano, mezzo-soprano, contralto, countertenor, tenor, baritone, bass |
| Age | Required for age-filtered matching | Exact integer; do not collect date of birth |
| Interests | Required for matching | competitions, opera-house auditions, young artist programs, masterclasses |
| Newsletter consent | Separate record | Preserve source, timestamp, and policy version |
| Personalized recommendations consent | Separate record | Must be affirmative and revocable |
| Created/updated timestamps | System fields | Needed for account and retention management |

## Storage and security

- Use a dedicated structured data store (Cloudflare D1 is the preferred candidate) after the account, region, access, backup, and retention configuration have been reviewed.
- Never store profile records in `CONTENT_DRAFTS`.
- No public endpoint may list or retrieve profiles by email.
- Verify email ownership before attaching a profile to a newsletter subscriber.
- Use opaque, expiring, single-use tokens for profile completion and account-management links; store only token hashes.
- Validate all fields server-side, enforce request-size limits, rate-limit public endpoints, and add anti-abuse protection.
- Restrict profile reads to authenticated administrative or matching workflows. Do not expose subscriber email addresses in the operations dashboard.
- Provide user-facing access, correction, withdrawal, and deletion processes.
- Define a retention period and deletion behavior before collecting real profiles.

## Matching behavior

- Match only opportunities that are official, verified, published, and still open.
- Exclude explicit voice and age mismatches.
- Clearly flag missing official eligibility details instead of claiming a match.
- Do not send personalized emails automatically in the first release. First show matches in a private user-facing page or prepare a reviewable recommendation draft.

## Rollout sequence

1. Keep Buttondown and the existing newsletter subscription flow unchanged.
2. Finalize the privacy notice, data-controller identity/contact details, purposes, lawful bases, retention period, and consent wording for this independent personal project.
3. Provision a dedicated profile database and secrets without importing existing subscribers.
4. Build and test email verification, optional profile completion, consent recording, account update/deletion, and rate limits using synthetic test data.
5. Run a private beta with explicit user approval.
6. Only then consider inviting existing subscribers, after checking the lawful basis and scope of their original consent.

## Launch blockers

Do not collect real profile data until the project operator's data-controller disclosure and contact details, privacy notice, consent wording, retention period, and user-rights process are finalized. Do not assume that an existing newsletter subscription automatically authorizes personalized profiling or additional invitation emails.
