import unittest

from collect_repertoire_candidates import candidate_id, make_candidate, normalized_title


class RepertoireCandidateTests(unittest.TestCase):
    def test_title_normalization_is_accent_and_punctuation_tolerant(self):
        self.assertEqual(normalized_title("La donna è mobile!"), "la donna mobile")

    def test_candidate_id_is_stable_for_same_title_and_page(self):
        first = candidate_id("La Traviata · Atto I · Scena I", "La traviata/Atto I")
        second = candidate_id("La Traviata · Atto I · Scena I", "La traviata/Atto I")
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("wikisource-"))

    def test_candidate_is_not_marked_for_publication(self):
        candidate = make_candidate(
            {
                "title": "La traviata · Atto I · Scena I",
                "page": "La traviata/Atto I",
                "work": "La traviata",
                "composer": "Giuseppe Verdi",
                "librettist": "Francesco Maria Piave",
                "body": "A sufficiently long scene text.",
            },
            "2026-11-13T08:00:00+01:00",
        )
        self.assertEqual(candidate["review_status"], "pending")
        self.assertEqual(candidate["publication_status"], "candidate")
        self.assertIn("并非已确认", candidate["summary"])
        self.assertEqual(candidate["voice"], "待核验")


if __name__ == "__main__":
    unittest.main()
