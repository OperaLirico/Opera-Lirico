import datetime as dt
import html
import tempfile
import unittest
from pathlib import Path

from weekly_digest import build_digest, eligible_items, parse_deadline


class WeeklyDigestTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime.fromisoformat("2026-11-10T12:00:00+01:00")

    def item(self, **updates):
        value = {
            "id": "sample", "title": "Sample <Call>", "opportunity_type": "vocal_competition",
            "source_name": "Official Org", "source_url": "https://example.org",
            "announcement_url": "https://example.org/call", "publisher_status": "official",
            "review_status": "verified", "publication_status": "published",
            "application_deadline_at": "2026-11-20T18:00:00+01:00",
            "voice_types": ["tenor"], "eligibility_summary": "Age 18+ & eligible."
        }
        value.update(updates)
        return value

    def test_strictly_filters_non_verified_and_expired(self):
        records = [
            self.item(),
            self.item(id="third-party", publisher_status="third_party"),
            self.item(id="pending", review_status="pending_manual_review"),
            self.item(id="draft", publication_status="draft"),
            self.item(id="expired", application_deadline_at="2026-11-01T00:00:00+01:00"),
            self.item(id="bad-date", application_deadline_at="not-a-date"),
        ]
        self.assertEqual([x["id"] for x in eligible_items(records, self.now)], ["sample"])

    def test_sorts_by_deadline(self):
        records = [
            self.item(id="later", application_deadline_at="2026-11-22T00:00:00+01:00"),
            self.item(id="earlier", application_deadline_at="2026-11-12T00:00:00+01:00"),
        ]
        self.assertEqual([x["id"] for x in eligible_items(records, self.now)], ["earlier", "later"])

    def test_html_escapes_untrusted_text(self):
        _, rendered, _ = build_digest([self.item()], self.now)
        self.assertIn("Sample &lt;Call&gt;", rendered)
        self.assertIn("Age 18+ &amp; eligible.", rendered)
        self.assertNotIn("<Call>", rendered)

    def test_empty_digest_is_valid(self):
        _, rendered, plain = build_digest([], self.now)
        self.assertIn("本期暂无符合条件的信息", rendered)
        self.assertIn("本期暂无符合条件的信息", plain)

    def test_naive_deadline_is_rejected(self):
        self.assertIsNone(parse_deadline("2026-11-20T18:00:00"))


if __name__ == "__main__":
    unittest.main()
