import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExtractionBenchmarkTemplateTests(unittest.TestCase):
    def test_template_is_30_unique_official_source_cases_and_unlabelled(self):
        policies = json.loads((ROOT / "data/source_fetch_policies.json").read_text(encoding="utf-8"))
        urls = [x["url"] for x in policies["entries"] if x.get("url", "").startswith(("https://", "http://"))]
        self.assertGreaterEqual(len(set(urls)), 30)
        # Validate the generator's contract without writing into the repository.
        source = (ROOT / "build_extraction_benchmark.py").read_text(encoding="utf-8")
        self.assertIn("TARGET_CASES = 30", source)
        self.assertIn('"status": "awaiting_manual_annotation"', source)
        self.assertIn('"evidence_quote": None', source)
        self.assertIn('"reviewed_at": None', source)
        self.assertIn("No page fetching, AI inference, API calls", source)

    def test_benchmark_is_not_wired_to_production_publishing(self):
        source = (ROOT / "build_extraction_benchmark.py").read_text(encoding="utf-8")
        self.assertNotIn("data/opportunities.json", source)
        self.assertNotIn("publication_status", source)
        self.assertNotIn("Gemini", source)


if __name__ == "__main__":
    unittest.main()
