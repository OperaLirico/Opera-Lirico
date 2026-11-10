import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "pdf-parser"))
import run_docling_evaluation as pdf_eval


class DoclingEvaluationSignalTests(unittest.TestCase):
    def test_instrument_name_is_not_mislabelled_as_a_voice_classification(self):
        evidence = pdf_eval.evidence_for_pages({2: "BASSO TUBA appears in the instrument list."})
        signals = {item["signal"] for item in evidence}
        self.assertIn("voice_term_candidates", signals)
        self.assertIn("instrument_context", signals)
        self.assertNotIn("vocal_context", signals)

    def test_vocal_role_context_is_kept_as_separate_evidence(self):
        evidence = pdf_eval.evidence_for_pages({4: "Artisti del coro: contralto e tenore."})
        signals = {item["signal"] for item in evidence}
        self.assertIn("voice_term_candidates", signals)
        self.assertIn("vocal_context", signals)

    def test_evidence_always_keeps_page_number_and_short_excerpt(self):
        evidence = pdf_eval.evidence_for_pages({7: "Scadenza della domanda entro il 4 dicembre 2026."})
        self.assertTrue(evidence)
        self.assertTrue(all(item["page_no"] == 7 for item in evidence))
        self.assertTrue(all(len(item["excerpt"]) <= 320 for item in evidence))


if __name__ == "__main__":
    unittest.main()
