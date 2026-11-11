# Weekly source coverage audit

- Cycle: 2026-W46
- Started: 2026-11-11T11:21:19+01:00
- Last updated: 2026-11-11T11:22:51+01:00
- Status: **in_progress**
- Coverage: **24/45** checked; 21 remaining
- Failed/restricted/extraction errors: 4 (restricted: 0)
- Change comparison: first baseline; no previous complete weekly scan exists yet
- Sources with anomalies: 3
- Registered sources: 23; candidate queue entries: 1
- Source review classifications: auto_approved_official=12, auto_approved_third_party=2, irrelevant_candidate=9, needs_review=1
- Official + relevant: 12
- Third-party + relevant: 1
- Needs review / irrelevant / unclassified: 10
- Inventory SHA-256: 51e30a921773c00e9a2b8f6092d1dcb4ac549bd90a7a0b6f050eaec5bcdd3fec (inventory identity only)

This scan checks page access and normalized text changes. A successful HTTP response is not proof of official identity, opportunity validity, or complete announcement capture. Text hashes are not publisher signatures.
Keyword/vocal signals are discovery clues only. Source identity and relevance are reported separately from HTTP reachability; source-level approval does not approve every notice on a mixed-purpose page.

## Exceptions and changes

### Teatro Lirico Sperimentale di Spoleto (source-10)
- URL: https://www.tls-belli.it/bandi_e_avvisi/
- Status: error / HTTP None
- Last success: not yet successful
- Anomalies: none
- Error: Timeout: Failed to perform, curl: (28) Connection timed out after 25000 milliseconds. See https://curl.se/libcurl/c/libcurl-errors.html first for more details.

### Lavora con noi - Fondazione Aida (source-115)
- URL: https://www.fondazioneaida.it/lavora-con-noi/
- Status: extraction_error / HTTP 202
- Last success: not yet successful
- Anomalies: empty_extraction

### Audizioni attori e attrici per la commedia brillante "Napule è" (source-117)
- URL: https://www.attoricasting.it/casting-teatro/audizioni-attori-e-attrici-per-la-commedia-brillante-napule-e/91421/
- Status: extraction_error / HTTP 202
- Last success: not yet successful
- Anomalies: empty_extraction

### Concorsi 2026 / Primo Oboe - Orchestra della Toscana (source-120)
- URL: https://www.orchestradellatoscana.it/concorsi-2026-primo-oboe/
- Status: extraction_error / HTTP 202
- Last success: not yet successful
- Anomalies: empty_extraction

## Coverage limitations

- Pending candidates are monitored separately and are not promoted to approved sources by this scan.
- 403/429, login walls, CAPTCHA and unavailable pages are recorded as monitoring blind spots; no bypass is attempted.
- A page with no vocal keyword signal is an anomaly clue, not proof that the institution has no current opportunity.
- A vocal keyword signal does not establish that a page or individual notice is relevant to classical singers.
