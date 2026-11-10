# Isolated PDF parser evaluation

This directory is deliberately isolated from the production opportunity pipeline.

## Current state

- Production mirrors selected official admission PDFs into data/pdfs/.
- audit_pdf_integrity.py records local file size, PDF magic bytes and SHA-256.
- SHA-256 establishes byte consistency only. It does not prove who published a PDF.
- No publisher digital signature is currently marked as verified.
- Docling is pinned only in this isolated experiment; it is not part of production requirements.
- The evaluation workflow is limited to this experiment branch or manual dispatch and uploads a report artifact only.

## Docling pilot

Run the evaluation script after installing requirements.txt, or run the isolated GitHub Actions workflow. It checks each selected local mirror against the existing SHA-256 manifest before parsing.

The report records Docling version, file hash, conversion status and runtime; page count, text-provenance coverage, table count and low-text page flags; and page-numbered snippets for dates, voice types, deadlines, fees, eligibility, application terms and repertoire.

Low-text pages are review flags only. They do not prove that a page is scanned. All extraction remains pending_manual_review, is_verified=false, and ineligible for publication.

## Safe evaluation sequence

1. Keep the original file, official URL, retrieval timestamp, byte size and SHA-256 unchanged.
2. Run Docling only in this isolated experiment; do not connect it to production data writes.
3. Compare extracted text and fields against manually checked page-level evidence.
4. Record page numbers, short evidence excerpts, confidence and parser version.
5. Only consider a production integration after repeatable tests show acceptable precision and recall on representative real samples.

## Explicit non-goals

- No OCR result is automatically published.
- No signature status is inferred from SHA-256, filename, domain, or a successful HTTP response.
- No proxy, stealth, login session, paid parser service or access-control bypass is used.
