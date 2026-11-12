---
name: pdf-bando-extraction
description: Extract structured audition and conservatory requirements from official Italian PDF regulations.
---

# Official PDF / bando extraction

1. Preserve the original PDF URL and downloaded bytes; record file size, content type, and SHA-256.
2. Extract text with the existing parser first. If the PDF is scanned or extraction is incomplete, run OCR or the isolated Docling evaluation. Do not replace the production parser solely because a pilot performs better on one sample.
3. Keep page numbers for every extracted fact.
4. Extract dates, time zones, age limits, voice types, repertoire, application documents, fees, payment instructions, and submission channels into separate fields.
5. Compare extracted text with page images for tables, signatures, stamps, handwritten notes, and layout-sensitive information.
6. Mark low-confidence, conflicting, or missing fields for manual review. Never invent a value to complete a schema.
7. Keep experimental parsers isolated until a representative evaluation set demonstrates better field-level accuracy.
