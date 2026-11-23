# Weekly source coverage audit

- Cycle: 2026-W48
- Started: 2026-11-23T16:43:50+01:00
- Last updated: 2026-11-23T16:45:38+01:00
- Status: **in_progress**
- Coverage: **36/45** checked; 9 remaining
- Failed/restricted/extraction errors: 4 (restricted: 1)
- Change comparison: first baseline; no previous complete weekly scan exists yet
- Sources with anomalies: 3
- Registered sources: 35; candidate queue entries: 1
- Source review classifications: auto_approved_official=20, auto_approved_third_party=6, duplicate_candidate=1, irrelevant_candidate=7, needs_review=2
- Official + relevant: 20
- Third-party + relevant: 5
- Needs review / irrelevant / unclassified: 9
- Duplicate candidates (registered): 1
- Inventory SHA-256: 27f13efcba9e91a843513c709ebf9a3eb96089e69020d8d01b803607e6c07780 (inventory identity only)

This scan checks page access and normalized text changes. A successful HTTP response is not proof of official identity, opportunity validity, or complete announcement capture. Text hashes are not publisher signatures.
Keyword/vocal signals are discovery clues only. Source identity and relevance are reported separately from HTTP reachability; source-level approval does not approve every notice on a mixed-purpose page.

## Exceptions and changes

### Teatro Lirico Sperimentale di Spoleto (source-10)
- URL: https://www.tls-belli.it/
- Status: restricted / HTTP 200
- Last success: not yet successful
- Anomalies: none

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
