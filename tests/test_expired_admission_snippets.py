import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExpiredAdmissionSnippetTests(unittest.TestCase):
    def test_academic_year_boundaries_and_multi_year_programmes(self):
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        start = app.index("function isExpiredAcademicSnippet(text){")
        end = app.index("\nfunction visibleCurrentLines", start)
        function_source = app[start:end]
        script = function_source + """
const samples = [
  ["2024–25 admission notice", true],
  ["2025/26 ammissione", true],
  ["2026/27 admission", false],
  ["2025–2027 multi-year admission programme", false],
  ["No new 2026 intake has been announced", false],
  ["2025 admission deadline", true]
];
console.log(JSON.stringify(samples.map(([text]) => isExpiredAcademicSnippet(text))));
"""
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            json.loads(result.stdout),
            [True, True, False, False, False, True],
        )


if __name__ == "__main__":
    unittest.main()
