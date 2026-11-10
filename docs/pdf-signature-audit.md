# PDF signature evidence audit

`audit_pdf_signatures.py` uses Poppler's `pdfsig` to inspect the local PDF mirrors listed in `.github/audits/pdf-integrity-manifest.json`.

It reports four distinct layers:
1. **Signature presence** — whether a PDF signature field was detected.
2. **Signature integrity** — whether Poppler reports the cryptographic signature as valid or invalid.
3. **Certificate trust** — whether Poppler reports the signing certificate as trusted, untrusted/unknown or inconclusive.
4. **Publisher identity** — always `not_verified` until a certificate subject is independently mapped to the official institution using a trusted publisher identity record.

A trusted certificate is not automatically the institution's certificate. SHA-256 manifest equality proves byte consistency only. This audit is read-only and never changes `publisher_signature_status` in the PDF manifest or opportunity records.

The monthly GitHub Actions workflow installs `poppler-utils` and writes a report to `.github/audits/pdf-signature-audit-latest.json` and `.md`. No external signature service, credential, paid product or production publishing path is used.
