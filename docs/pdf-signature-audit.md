# PDF signature evidence audit

`audit_pdf_signatures.py` uses Poppler's `pdfsig` to inspect the local PDF mirrors listed in `.github/audits/pdf-integrity-manifest.json`.

It reports four distinct layers:
1. **Signature presence** — whether a PDF signature field was detected.
2. **Signature integrity** — whether Poppler reports the cryptographic signature as valid or invalid. A `Digest Mismatch` is classified as invalid, not as a parser/tool failure.
3. **Certificate trust** — whether Poppler reports the signing certificate as trusted, untrusted/unknown or inconclusive.
4. **Publisher identity** — always `not_verified` until a certificate subject is independently mapped to the official institution using a trusted publisher identity record.

The first audit run detected signature fields in two PDFs: one contained two signatures reported cryptographically valid, but both certificate issuers were unknown; the second PDF had a signature with `Digest Mismatch`. The signer subject on one valid signature names Conservatorio di Musica Arrigo Pedrollo di Vicenza, but the certificate chain was not trusted, so publisher identity remains unverified. A digest mismatch means the signature does not validate against the PDF bytes; it does not by itself prove who changed the file or when.

Poppler may return a non-zero exit code for an unsigned PDF. When its output explicitly says the PDF contains no signatures, the audit records `success_no_signature`, not a tool error. Unexpected output and missing tools remain errors/inconclusive.

A trusted certificate is not automatically the institution's certificate. SHA-256 manifest equality proves byte consistency only. This audit is read-only and never changes `publisher_signature_status` in the PDF manifest or opportunity records.

The monthly GitHub Actions workflow installs `poppler-utils` and writes a report to `.github/audits/pdf-signature-audit-latest.json` and `.md`. No external signature service, credential, paid product or production publishing path is used.
