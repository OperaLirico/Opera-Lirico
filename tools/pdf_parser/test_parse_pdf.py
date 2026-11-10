import unittest

from parse_pdf import extract_candidates


class CandidateExtractionTests(unittest.TestCase):
    def test_extracts_admission_signals_as_candidates(self):
        text = """
        # Bando di ammissione 2026/2027
        Le domande devono essere presentate entro il 30 giugno 2026.
        Il candidato non deve aver compiuto 30 anni.
        Sono ammessi soprano, tenore e baritono.
        Il programma musicale prevede due arie d'opera.
        La prova pratica si svolgerà presso la sede.
        """
        result = extract_candidates(text)
        self.assertTrue(result["deadline_candidates"])
        self.assertTrue(result["age_limit_candidates"])
        self.assertEqual(len(result["voice_type_candidates"]), 1)
        self.assertTrue(result["requirement_candidates"])
        self.assertTrue(result["date_candidates"])

    def test_ignores_unrelated_lines(self):
        result = extract_candidates("Benvenuti sul sito del conservatorio.\nCookie policy.")
        self.assertEqual(result["deadline_candidates"], [])
        self.assertEqual(result["age_limit_candidates"], [])
        self.assertEqual(result["voice_type_candidates"], [])
        self.assertEqual(result["requirement_candidates"], [])


if __name__ == "__main__":
    unittest.main()
