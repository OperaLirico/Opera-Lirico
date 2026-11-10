import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import audit_pdf_signatures as audit


class PdfSignatureParsingTests(unittest.TestCase):
    def test_valid_signature_and_trusted_certificate_do_not_verify_publisher_identity(self):
        output = """Digital Signature Info of: sample.pdf
Signature #1:
  - Signature Field Name: Signature1
  - Signer Certificate Common Name: Mario Rossi
  - Signer full Distinguished Name: CN=Mario Rossi,O=Example Conservatory
  - Signing Time: Nov 10 2026 10:00:00
  - Signing Hash Algorithm: SHA-256
  - Signature Type: ETSI.CAdES.detached
  - Signature Validation: Signature is Valid.
  - Certificate Validation: Certificate is Trusted.
"""
        sig = audit.parse_pdfsig_output(output)["signatures"][0]
        self.assertEqual(sig["signature_integrity_status"], "valid")
        self.assertEqual(sig["certificate_trust_status"], "trusted")
        self.assertEqual(sig["publisher_identity_status"], "not_verified")

    def test_unknown_certificate_is_not_reported_as_trusted(self):
        output = """Signature #1:
  - Signer Certificate Common Name: Unknown Signer
  - Signature Validation: Signature is Valid.
  - Certificate Validation: Certificate issuer is unknown.
"""
        sig = audit.parse_pdfsig_output(output)["signatures"][0]
        self.assertEqual(sig["signature_integrity_status"], "valid")
        self.assertEqual(sig["certificate_trust_status"], "untrusted_or_unknown")

    def test_invalid_signature_is_reported_separately(self):
        output = """Signature #2:
  - Signature Validation: Signature is Invalid.
  - Certificate Validation: Certificate is Trusted.
"""
        sig = audit.parse_pdfsig_output(output)["signatures"][0]
        self.assertEqual(sig["signature_integrity_status"], "invalid")
        self.assertEqual(sig["certificate_trust_status"], "trusted")

    def test_no_signature_is_not_a_tool_error(self):
        parsed = audit.parse_pdfsig_output("File 'sample.pdf' does not contain any signatures.")
        self.assertEqual(parsed, {"signature_presence": "not_detected", "signatures": []})


if __name__ == "__main__":
    unittest.main()
