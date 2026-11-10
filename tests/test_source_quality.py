import unittest

import grow_sources
import scrape_sources


class PreserveLastGoodTests(unittest.TestCase):
    def test_failed_refresh_keeps_previous_extract(self):
        previous = {
            "number": 1,
            "source": "Opera House",
            "url": "https://example.org/auditions",
            "status": "ok",
            "checked_at": "2026-11-09T10:00:00+01:00",
            "relevant_lines": ["Audizioni per cantanti lirici"],
            "consecutive_failures": 0,
        }
        failed = {
            "number": 1,
            "source": "Opera House",
            "url": "https://example.org/auditions",
            "status": "http_error",
            "http_status": 403,
            "title": "",
            "relevant_lines": [],
            "error": "HTTP 403",
        }
        result = scrape_sources.preserve_last_good(
            previous, failed, "2026-11-10T10:00:00+01:00"
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["relevant_lines"], previous["relevant_lines"])
        self.assertTrue(result["stale"])
        self.assertEqual(result["last_attempt_http_status"], 403)
        self.assertEqual(result["consecutive_failures"], 1)
        self.assertEqual(result["checked_at"], previous["checked_at"])

    def test_successful_refresh_replaces_snapshot_and_resets_failures(self):
        previous = {"status": "ok", "consecutive_failures": 3}
        current = {
            "number": 1,
            "status": "ok",
            "title": "New notice",
            "relevant_lines": ["Audizioni per tenori"],
        }
        result = scrape_sources.preserve_last_good(
            previous, current, "2026-11-10T10:00:00+01:00"
        )
        self.assertFalse(result["stale"])
        self.assertEqual(result["consecutive_failures"], 0)
        self.assertEqual(result["last_success_at"], "2026-11-10T10:00:00+01:00")

    def test_first_failure_is_recorded_without_inventing_snapshot(self):
        current = {"status": "error", "error": "timeout", "relevant_lines": []}
        result = scrape_sources.preserve_last_good(
            None, current, "2026-11-10T10:00:00+01:00"
        )
        self.assertTrue(result["stale"])
        self.assertEqual(result["last_attempt_status"], "error")
        self.assertEqual(result["relevant_lines"], [])

    def test_voice_related_audition_passes_to_review_queue(self):
        probe = {
            "status": "ok",
            "source": "Opera competition",
            "title": "International opera singing competition",
            "relevant_lines": [
                "Concorso internazionale di canto lirico",
                "Audizioni per soprano e tenore",
                "Application deadline 30 November 2026",
            ],
        }
        self.assertIsNone(
            grow_sources.candidate_rejection_reason(probe, "https://example.org/competition")
        )

    def test_instrument_only_audition_is_rejected(self):
        probe = {
            "status": "ok",
            "source": "Orchestra competition",
            "title": "Concorso 2026 - Primo Oboe",
            "relevant_lines": [
                "Concorso per primo oboe",
                "Audizione per strumentisti",
                "Prova finale il 15 dicembre 2026",
            ],
        }
        self.assertEqual(
            grow_sources.candidate_rejection_reason(probe, "https://example.org/oboe"),
            "no_vocal_or_opera_signal",
        )

    def test_review_labels_survive_successful_refresh(self):
        previous = {
            "review_status": "legacy_unreviewed",
            "publisher_status": "unverified",
        }
        fresh = {"status": "ok", "title": "Updated page"}
        result = grow_sources.carry_review_metadata(fresh, previous)
        self.assertEqual(result["review_status"], "legacy_unreviewed")
        self.assertEqual(result["publisher_status"], "unverified")

    def test_generic_actor_casting_is_rejected(self):
        probe = {
            "status": "ok",
            "source": "Casting",
            "title": "Audizioni attori e attrici",
            "relevant_lines": [
                "Audizioni per attori",
                "Candidature aperte",
                "Selezione per spettacolo teatrale",
            ],
        }
        self.assertEqual(
            grow_sources.candidate_rejection_reason(probe, "https://example.org/casting"),
            "no_vocal_or_opera_signal",
        )


if __name__ == "__main__":
    unittest.main()
