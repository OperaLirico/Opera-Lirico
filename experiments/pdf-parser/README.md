# Isolated PDF parser evaluation

This directory is deliberately isolated from the production opportunity pipeline.

## Current state

- Production currently mirrors selected official admission PDFs into data/pdfs/.
- audit_pdf_integrity.py records local file size, PDF magic bytes and SHA-256.
- SHA-256 establishes byte consistency only. It does not prove who published a PDF.
- No publisher digital signature is currently marked as verified.
- No Docling dependency is installed in the production requirements.
- No validated Docling extraction prototype or representative raw-PDF benchmark is present on the current main branch.

## Safe evaluation sequence

1. Select a small set of real, publicly available official PDFs with different layouts (text PDF, table-heavy PDF, scanned PDF).
2. Keep the original file, official URL, retrieval timestamp, byte size and SHA-256 unchanged.
3. Run Docling only in this isolated experiment; do not connect it to production data writes.
4. Compare extracted text and fields against manually checked page-level evidence: dates, voice types, eligibility, fees, repertoire, application URL and deadline.
5. Record page numbers, short evidence excerpts, confidence and parser version.
6. Every extracted record must remain pending_manual_review and is_verified=false.
7. Only consider a production integration after repeatable tests show acceptable precision and recall on the real sample set.

## Explicit non-goals

- No OCR result is automatically published.
- No signature status is inferred from SHA-256, filename, domain, or a successful HTTP response.
- No proxy, stealth, login session, paid parser service or access-control bypass is used.
