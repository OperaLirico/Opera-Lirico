import unittest

from discover_masterclasses import canonical_url, has_future_date, make_candidate, slug


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

    def test_rejects_generic_academy_page_with_navigation_keywords(self):
        candidate = make_candidate(
            self.source,
            "https://example.org/",
            "Academy Home",
            "Masterclasses for opera singers and voice students. Applications for 2027.",
            "2026-11-12T10:00:00+01:00",
        )
        self.assertIsNone(candidate)

    def test_future_date_filter_rejects_expired_and_accepts_upcoming_dates(self):
        self.assertFalse(has_future_date("10 Novembre 2026"))
        self.assertTrue(has_future_date("30 Novembre 2026"))

    def test_canonical_url_removes_fragment(self):
        self.assertEqual(
            canonical_url("https://example.org/masterclass#details"),
            "https://example.org/masterclass",
        )

    def test_ignores_generic_navigation_labels_and_uses_page_title(self):
        candidate = make_candidate(
            self.source,
            "https://example.org/course-2027",
            "Masterclass di Canto con Anna Rossi",
            "Opera singers, soprano and tenor. 12 July 2027. Applications open.",
            "2026-11-12T10:00:00+01:00",
            "Salta al contenuto",
        )
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["title_hint"], "Masterclass di Canto con Anna Rossi")

    def test_rejects_generic_listing_page_title(self):
        candidate = make_candidate(
            self.source,
            "https://example.org/masterclasses",
            "MASTERCLASS - Test Academy",
            "Masterclasses for opera singers and voice students. 12 July 2027.",
            "2026-11-12T10:00:00+01:00",
        )
        self.assertIsNone(candidate)

    def test_deduplicates_fragment_urls_and_preserves_review(self):
        from discover_masterclasses import deduplicate_candidates
        base = {
            "source_name": "Test Academy",
            "source_url": "https://example.org/masterclass#main",
            "checked_at": "2026-11-12T10:00:00+01:00",
            "review_status": "pending_manual_review",
            "review_notes": "",
        }
        reviewed = {
            **base,
            "candidate_id": "aaaaaaaaaaaa",
            "source_url": "https://example.org/masterclass#details",
            "checked_at": "2026-11-12T09:00:00+01:00",
            "review_status": "verified_pending_publication",
            "review_notes": "Checked against organizer page",
        }
        fresh = {**base, "candidate_id": "bbbbbbbbbbbb"}
        result = deduplicate_candidates([reviewed, fresh])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source_url"], "https://example.org/masterclass")
        self.assertEqual(result[0]["review_status"], "verified_pending_publication")
        self.assertEqual(result[0]["review_notes"], "Checked against organizer page")

    def test_slug_is_stable_and_safe(self):
        self.assertEqual(slug("Verdi Marathon 2027"), "verdi-marathon-2027")


if __name__ == "__main__":
    unittest.main()
