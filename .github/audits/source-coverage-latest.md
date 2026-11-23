# Weekly source coverage audit

- Cycle: 2026-W48
- Started: 2026-11-23T16:32:35+01:00
- Last updated: 2026-11-23T16:33:31+01:00
- Status: **in_progress**
- Coverage: **24/46** checked; 22 remaining
- Failed/restricted/extraction errors: 2 (restricted: 0)
- Change comparison: first baseline; no previous complete weekly scan exists yet
- Sources with anomalies: 0
- Registered sources: 22; candidate queue entries: 2
- Source review classifications: auto_approved_official=11, auto_approved_third_party=3, duplicate_candidate=1, irrelevant_candidate=7, needs_review=2
- Official + relevant: 10
- Third-party + relevant: 2
- Needs review / irrelevant / unclassified: 9
- Duplicate candidates (registered): 1
- Inventory SHA-256: cb9ddd5656d6377347395744cc24959f6da47af7a1af716d2e0294027745d586 (inventory identity only)

This scan checks page access and normalized text changes. A successful HTTP response is not proof of official identity, opportunity validity, or complete announcement capture. Text hashes are not publisher signatures.
Keyword/vocal signals are discovery clues only. Source identity and relevance are reported separately from HTTP reachability; source-level approval does not approve every notice on a mixed-purpose page.

## Exceptions and changes

### Teatro Lirico Sperimentale di Spoleto — 81st International Singing Competition (candidate-2)
- URL: https://tls-belli.it/concorso-di-canto-2026/
- Status: error / HTTP None
- Last success: not yet successful
- Anomalies: none
- Error: CertificateVerifyError: Failed to perform, curl: (60) SSL: no alternative certificate subject name matches target hostname 'tls-belli.it'. See https://curl.se/libcurl/c/libcurl-errors.html first for more details.

### Teatro Lirico Sperimentale di Spoleto (source-10)
- URL: https://tls-belli.it/bandi_e_avvisi/
- Status: error / HTTP None
- Last success: not yet successful
- Anomalies: none
- Error: CertificateVerifyError: Failed to perform, curl: (60) SSL: no alternative certificate subject name matches target hostname 'tls-belli.it'. See https://curl.se/libcurl/c/libcurl-errors.html first for more details.

## Coverage limitations

- Pending candidates are monitored separately and are not promoted to approved sources by this scan.
- 403/429, login walls, CAPTCHA and unavailable pages are recorded as monitoring blind spots; no bypass is attempted.
- A page with no vocal keyword signal is an anomaly clue, not proof that the institution has no current opportunity.
- A vocal keyword signal does not establish that a page or individual notice is relevant to classical singers.
