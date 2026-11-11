import unittest
from datetime import date

from content_engine.matcher import match_opportunities, validate_profile


BASE = {
    "id": "tenor-call",
    "title": "Tenor Audition",
    "opportunity_type": "choir",
    "voice_types": ["tenor"],
    "publisher_status": "official",
    "review_status": "verified",
    "publication_status": "published",
    "application_deadline_at": "2026-12-01T23:59:00+01:00",
    "age_min": 18,
    "age_max": 35,
    "source_url": "https://example.org/call",
}


class MatcherTests(unittest.TestCase):
    def test_matches_voice_interest_and_age(self):
        profile = {"voice_type": "tenor", "age": 30, "interests": ["opera_house_auditions"]}
        result = match_opportunities(profile, [BASE], today=date(2026, 11, 12))
        self.assertEqual([x["id"] for x in result], ["tenor-call"])
        self.assertEqual(result[0]["voice_match"], "match")
        self.assertEqual(result[0]["age_eligibility"], "within_published_limits")

    def test_excludes_wrong_voice(self):
        profile = {"voice_type": "soprano", "age": 30, "interests": ["opera_house_auditions"]}
        self.assertEqual(match_opportunities(profile, [BASE], today=date(2026, 11, 12)), [])

    def test_excludes_age_outside_limits(self):
        profile = {"voice_type": "tenor", "age": 36, "interests": ["opera_house_auditions"]}
        self.assertEqual(match_opportunities(profile, [BASE], today=date(2026, 11, 12)), [])

    def test_excludes_expired_and_unverified(self):
        expired = {**BASE, "application_deadline_at": "2026-11-01T00:00:00+01:00"}
        unverified = {**BASE, "review_status": "pending"}
        profile = {"voice_type": "tenor", "age": 30, "interests": ["opera_house_auditions"]}
        self.assertEqual(match_opportunities(profile, [expired, unverified], today=date(2026, 11, 12)), [])

    def test_unspecified_voice_is_flagged_not_asserted_as_match(self):
        item = {**BASE, "voice_types": ["unspecified"]}
        profile = {"voice_type": "tenor", "age": 30, "interests": ["opera_house_auditions"]}
        result = match_opportunities(profile, [item], today=date(2026, 11, 12))
        self.assertEqual(result[0]["voice_match"], "unspecified")
        self.assertIn("建议申请前确认", result[0]["match_notes"][0])

    def test_profile_validation(self):
        with self.assertRaises(ValueError):
            validate_profile({"voice_type": "voice", "age": 30, "interests": ["competitions"]})
        with self.assertRaises(ValueError):
            validate_profile({"voice_type": "tenor", "age": True, "interests": ["competitions"]})


if __name__ == "__main__":
    unittest.main()
