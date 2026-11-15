import datetime as dt
import re
import unittest

from weekly_digest import (
    VOICE_FALLBACK_GUARDS,
    VOICE_ORDER,
    build_fallback_block,
    build_personalized_digest,
    build_voice_block,
    items_for_voice,
    subject_line,
)


class NewsletterVoiceSegmentationTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime.fromisoformat("2026-11-15T12:00:00+01:00")

    def item(self, **updates):
        value = {
            "id": "sample", "title": "Sample <Call>", "opportunity_type": "vocal_competition",
            "source_name": "Official Org", "source_url": "https://example.org",
            "announcement_url": "https://example.org/call", "publisher_status": "official",
            "review_status": "verified", "publication_status": "published",
            "application_deadline_at": "2026-11-20T18:00:00+01:00",
            "voice_types": ["tenor"], "eligibility_summary": "Age 18+ & eligible.",
        }
        value.update(updates)
        return value

    def test_voice_filter_matches_named_voice_and_open_to_all(self):
        records = [
            self.item(id="tenor-only", voice_types=["tenor"]),
            self.item(id="everyone", voice_types=["all_voices"]),
            self.item(id="soprano-only", voice_types=["soprano"]),
        ]
        self.assertEqual(
            [x["id"] for x in items_for_voice(records, self.now, "tenor")],
            ["tenor-only", "everyone"],
        )

    def test_voice_filter_still_honours_verification_gates(self):
        records = [self.item(id="pending", review_status="pending_manual_review", voice_types=["tenor"])]
        self.assertEqual(items_for_voice(records, self.now, "tenor"), [])

    def test_all_voices_selector_returns_every_verified_item(self):
        records = [self.item(id="a"), self.item(id="b", voice_types=["bass"])]
        self.assertEqual(len(items_for_voice(records, self.now, "all_voices")), 2)

    def test_personalized_digest_has_one_guard_per_voice(self):
        _, body, _ = build_personalized_digest([self.item()], self.now)
        guards = re.findall(r'{% if subscriber\.metadata\.voice == "([a-z_]+)" %}', body)
        # Named voices first, then the "声部未注明" fallback (its guard uses == too);
        # the empty-metadata fallback is checked separately below.
        self.assertEqual(guards, list(VOICE_ORDER) + ["all_voices", "unspecified"])
        total_blocks = len(VOICE_ORDER) + 1 + len(VOICE_FALLBACK_GUARDS)
        self.assertEqual(body.count("{% endif %}"), total_blocks)
        for guard in VOICE_FALLBACK_GUARDS:
            self.assertIn("{% if " + guard + " %}", body)
        # No stray braces that Buttondown's template engine would try to parse.
        self.assertIsNone(re.search(r'(?<!%|\{)\{[^{%]', body))

    def test_fallback_block_carries_the_whole_list(self):
        block = build_fallback_block(
            [self.item(id="tenor-only", voice_types=["tenor"],
                       application_deadline_at="2026-11-18T18:00:00+01:00"),
             self.item(id="bass-only", voice_types=["bass"],
                       application_deadline_at="2026-11-24T18:00:00+01:00")],
            self.now,
        )
        self.assertIn("还没填声部", block)
        self.assertEqual(block.count("<article>"), 2)

    def test_personalized_digest_escapes_untrusted_text(self):
        _, body, _ = build_personalized_digest([self.item()], self.now)
        self.assertIn("Sample &lt;Call&gt;", body)
        self.assertNotIn("<Call>", body)

    def test_voice_block_reports_empty_state(self):
        block = build_voice_block([self.item(voice_types=["soprano"])], self.now, "bass")
        self.assertIn("本周没有新增点名男低音", block)
        self.assertNotIn("Sample", block)

    def test_personalized_digest_slug_is_voiced_and_stable(self):
        slug, _, _ = build_personalized_digest([], self.now)
        self.assertEqual(slug, "opera-lirico-weekly-2026-11-15-voiced")

    def test_subject_line_states_date_and_voice_intent(self):
        self.assertEqual(subject_line(self.now), "Opera Lirico 每周简报｜2026-11-15｜按你的声部")


if __name__ == "__main__":
    unittest.main()
