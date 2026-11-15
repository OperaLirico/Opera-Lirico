import json
import tempfile
import unittest
from datetime import timezone
from pathlib import Path
from unittest.mock import patch

from content_engine import auto_review


class AutoReviewSafetyTests(unittest.TestCase):
    def valid_draft(self):
        return {
            "title": "Opera masterclass",
            "caption": "A" * 160,
            "source_url": "https://www.wj-operamusic.academy/event",
            "category": "masterclass",
        }

    def test_empty_allowlist_never_auto_approves(self):
        ok, reasons = auto_review.judge(self.valid_draft(), set(), set())
        self.assertFalse(ok)
        self.assertTrue(any("白名单不可用" in reason for reason in reasons))

    def test_only_explicit_official_registry_entries_are_trusted(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            registry = data_dir / "masterclass_sources.json"
            registry.write_text(json.dumps({
                "sources": [
                    {"url": "https://official.example/events", "publisher_status": "official"},
                    {"url": "https://directory.example/list", "publisher_status": "third_party"},
                    {"url": "http://insecure.example/", "publisher_status": "official"},
                    {"url": "https://user:pass@credential.example/", "publisher_status": "official"},
                ]
            }), encoding="utf-8")
            with patch.object(auto_review, "ROOT", Path(tmp)):
                self.assertEqual(auto_review.official_hosts(), {"official.example"})

    def test_missing_registry_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(auto_review, "ROOT", Path(tmp)):
                self.assertEqual(auto_review.official_hosts(), set())

    def test_unlisted_domain_is_escalated(self):
        ok, reasons = auto_review.judge(self.valid_draft(), {"official.example"}, set())
        self.assertFalse(ok)
        self.assertTrue(any("不在明确核准" in reason for reason in reasons))

    def test_subdomain_of_official_host_is_allowed(self):
        draft = self.valid_draft()
        draft["source_url"] = "https://events.wj-operamusic.academy/page"
        ok, _ = auto_review.judge(draft, {"wj-operamusic.academy"}, set())
        self.assertTrue(ok)

    def test_url_with_embedded_credentials_is_rejected(self):
        draft = self.valid_draft()
        draft["source_url"] = "https://user:pass@wj-operamusic.academy/event"
        ok, reasons = auto_review.judge(draft, {"wj-operamusic.academy"}, set())
        self.assertFalse(ok)
        self.assertTrue(any("用户凭据" in reason for reason in reasons))

    def test_created_at_requires_timezone(self):
        self.assertIsNone(auto_review.parse_created_at(None))
        self.assertIsNone(auto_review.parse_created_at("not-a-date"))
        self.assertIsNone(auto_review.parse_created_at("2026-11-14T10:00:00"))
        parsed = auto_review.parse_created_at("2026-11-14T10:00:00+01:00")
        self.assertEqual(parsed.tzinfo, timezone.utc)

    def test_duplicate_caption_is_rejected(self):
        draft = self.valid_draft()
        ok, reasons = auto_review.judge(draft, {"wj-operamusic.academy"}, {
            auto_review.normalize(draft["caption"])[:120]
        })
        self.assertFalse(ok)
        self.assertTrue(any("重复" in reason for reason in reasons))


if __name__ == "__main__":
    unittest.main()
