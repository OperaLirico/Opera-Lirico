# OperaLab vocal score reader: implementation and rights gates

Date: 2026-11-24
Status: architecture decision; not yet implemented in the public UI.

## Product behavior

The repertoire page should let a singer open a score from an individual work record without confusing a work page, a scene/libretto, and a standalone aria. Each score record must identify the exact edition and the rights basis for the copy being displayed.

A score is eligible for an embedded viewer only when:
- the source file is HTTPS and the file is stable/reachable;
- the exact edition/source is identified;
- the rights status is verified for the territories in which OperaLab makes it available;
- the source attribution and rights-check date are recorded;
- the score is not merely a full opera scene accidentally collected as an aria.

Otherwise, show a clearly labelled external source link, or do not expose the score link if the source itself is not reliable. Do not download, mirror, OCR, or republish a scan just because it is publicly reachable. Public-domain status of a composition does not automatically prove that every modern edition or scan is reusable in every territory.

## Rendering engines

Use two engines according to the file format, not one engine for everything:

| Source format | Engine | Role |
| --- | --- | --- |
| PDF | Mozilla PDF.js | Render page-based publisher/library PDFs in the browser |
| MEI | Verovio JavaScript toolkit | Engrave structured notation into responsive SVG pages |
| MusicXML / MXL | Verovio JavaScript toolkit | Load supported MusicXML and render via its notation pipeline |
| External source page | Native link | Keep the user on the original library/publisher page |

Official implementation references:
- PDF.js is Mozilla's HTML5 PDF rendering/viewer project. Use its current official release and build a branded OperaLab presentation rather than exposing an unmodified viewer: https://mozilla.github.io/pdf.js/getting_started/
- Verovio's JavaScript toolkit renders MEI in the browser and supports MusicXML input/conversion: https://book.verovio.org/first-steps/ and https://book.verovio.org/interactive-notation/encoding-formats.html
- Verovio App demonstrates responsive/document score views and page navigation: https://www.verovio.org/app.html

## Data contract

`data/repertoire-score.schema.json` defines the score-source record. Keep score metadata separate from the core repertoire identity so that one work can have multiple editions and sources.

Important fields:
- `format`: pdf, mei, musicxml, mxl, or external_page;
- `source_url` and optional `file_url`;
- `edition_title`, `publisher`, `editor`, and `publication_year`;
- `rights_status`: public_domain_verified, permission_granted, licensed, link_only, or unknown;
- `rights_basis`, `territories`, and `rights_checked_at`;
- `access_mode` and `viewer_engine`.

The schema deliberately defaults to an external link. Embedded viewing requires a documented rights basis, territory list, review timestamp, file URL, and engine. Unknown rights never become an embedded score by default.

## User experience requirements

1. On a repertoire item, show a compact “乐谱” action only when a score source exists.
2. Embedded viewer opens in a dedicated, responsive reading surface with page navigation, zoom, loading/error states, and a return-to-work action.
3. Mobile view prioritizes readable single-page width and simple previous/next controls; avoid tiny two-page spreads.
4. Always show edition/source attribution and the rights/availability note near the viewer.
5. If the file fails to load, preserve the official source link and explain that the source may have changed.
6. Never imply that an external link is an embedded viewer or that a scene-level libretto candidate is a verified aria.

## Delivery phases

- Phase 1: validate the metadata schema against representative records; audit the current 16 curated repertoire items and classify each score source as link_only or rights-verified.
- Phase 2: implement PDF.js for a small set of explicitly cleared PDFs; test desktop and mobile loading, navigation, zoom, accessibility, and failures.
- Phase 3: add Verovio for MEI/MusicXML where structured score files are actually available; verify rendering fidelity and unsupported notation cases.
- Phase 4: connect the reader to search, voice filters, and work details without mixing candidate records into the curated catalogue.

## Explicit non-goals

- No automatic scraping or downloading of sheet-music scans.
- No assumption that IMSLP, Wikisource, or a public URL means every score edition is freely reusable.
- No automatic promotion of scene/libretto candidates into the aria catalogue.
- No score publication until the specific edition, file, territory, and rights basis have been checked.
