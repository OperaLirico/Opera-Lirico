import unittest

from discover_masterclasses import make_candidate, slug


class MasterclassDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.source = {
            "id": "test-source",
            "name": "Test Academy",
            "url": "https://example.org/masterclasses",
            "publisher_status": "official",
            "source_type": "organizer",
        }

    def test_detects_vocal_masterclass(self):
        candidate = make_candidate(
            self.source,
            "https://example.org/course-2027",
            "Summer Vocal Masterclass 2027",
            "Opera singers, soprano, tenor. 12 July 2027. Applications open.",
            "2026-11-12T10:00:00+01:00",
        )
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["review_status"], "pending_manual_review")
        self.assertEqual(candidate["publication_status"], "not_published")
        self.assertIn("2027", candidate["date_signals"])

    def test_rejects_non_vocal_masterclass(self):
        candidate = make_candidate(
            self.source,
            "https://example.org/piano",
            "Piano Masterclass 2027",
            "Masterclass for piano students and pianists.",
            "2026-11-12T10:00:00+01:00",
        )
        self.assertIsNone(candidate)

    def test_rejects_vocal_course_without_masterclass_signal(self):
        candidate = make_candidate(
            self.source,
            "https://example.org/choir",
            "Choir auditions",
            "Auditions for tenor and bass singers.",
            "2026-11-12T10:00:00+01:00",
        )
        self.assertIsNone(candidate)

    def test_slug_is_stable_and_safe(self):
        self.assertEqual(slug("Verdi Marathon 2027"), "verdi-marathon-2027")


if __name__ == "__main__":
    unittest.main()
