import unittest

import audit_opportunity_quality as audit


class OpportunityQualityObservabilityTests(unittest.TestCase):
    def test_missing_verification_timestamp_is_reported(self):
        records = [
            {"id": "missing", "checked_at": None},
            {"id": "invalid", "last_verified_at": "2026-11-15T10:00:00"},
            {"id": "valid", "last_verified_at": "2026-11-15T10:00:00+01:00"},
        ]
        findings = audit.missing_verification_timestamp(records)
        self.assertEqual([item["id"] for item in findings], ["missing", "invalid"])

    def test_invalid_url_schemes_and_credentials_are_reported(self):
        records = [{
            "id": "bad-links",
            "source_url": "http://example.org/source",
            "announcement_url": "https://user:pass@example.org/call",
            "application_url": "https://apply.example.org/form",
            "official_pdf_url": "javascript:alert(1)",
        }]
        findings = audit.invalid_urls(records)
        self.assertEqual(
            {(item["id"], item["field"]) for item in findings},
            {
                ("bad-links", "source_url"),
                ("bad-links", "announcement_url"),
                ("bad-links", "official_pdf_url"),
            },
        )

    def test_empty_optional_urls_are_not_reported_as_malformed(self):
        self.assertEqual(audit.invalid_urls([{
            "source_url": "https://example.org",
            "announcement_url": "",
            "application_url": None,
            "official_pdf_url": None,
        }]), [])

    def test_non_string_datetime_is_rejected_safely(self):
        self.assertIsNone(audit.parse_dt(12345))
        self.assertIsNone(audit.parse_dt("not-a-date"))
        self.assertIsNone(audit.parse_dt("2026-11-15T10:00:00"))


if __name__ == "__main__":
    unittest.main()
