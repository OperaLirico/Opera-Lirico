import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from audit_opportunity_quality import (
    deadline_is_expired,
    deadline_is_open,
    deadline_within_window,
    parse_date,
    parse_dt,
)
from audit_pdf_integrity import inspect_pdf


class AuditHelperTests(unittest.TestCase):
    def test_parse_rejects_naive_datetime(self):
        self.assertIsNone(parse_dt("2026-11-25T18:00:00"))

    def test_parse_accepts_rome_offset(self):
        value = parse_dt("2026-11-25T18:00:00+01:00")
        self.assertIsNotNone(value)
        self.assertEqual(value.utcoffset(), datetime(2026, 11, 25, 18, tzinfo=ZoneInfo("Europe/Rome")).utcoffset())

    def test_date_only_deadline_is_valid_and_never_assigned_a_time(self):
        value = "2026-12-09"
        self.assertEqual(parse_date(value), date(2026, 12, 9))
        self.assertIsNone(parse_date("2026-12-09T23:59:00+01:00"))
        today = datetime(2026, 12, 9, 12, 0, tzinfo=ZoneInfo("Europe/Rome"))
        record = {"application_deadline_date": value}
        self.assertTrue(deadline_is_open(record, today))
        self.assertFalse(deadline_is_expired(record, today))
        self.assertTrue(deadline_within_window(record, today, 7))
        earlier = datetime(2026, 12, 10, 0, 0, tzinfo=ZoneInfo("Europe/Rome"))
        self.assertTrue(deadline_is_expired(record, earlier))

    def test_pdf_integrity_checks_magic_and_hash(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.pdf"
            path.write_bytes(b"%PDF-1.7\nminimal test bytes")
            result = inspect_pdf(path)
            self.assertEqual(result["integrity_status"], "valid_pdf_bytes")
            self.assertEqual(len(result["sha256"]), 64)
            path.write_bytes(b"not a pdf")
            self.assertEqual(inspect_pdf(path)["integrity_status"], "invalid_pdf_bytes")


if __name__ == "__main__":
    unittest.main()
