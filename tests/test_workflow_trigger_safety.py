import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTriggerSafetyTests(unittest.TestCase):
    def test_daily_scrape_is_not_triggered_by_every_python_file(self):
        workflow = (ROOT / ".github" / "workflows" / "daily-scrape-and-publish.yml").read_text(encoding="utf-8")
        self.assertNotIn('      - "*.py"', workflow)
        self.assertNotIn('      - ".github/workflows/daily-scrape-and-publish.yml"', workflow)
        for path in (
            "scrape_sources.py", "grow_sources.py", "run_conservatori.py",
            "mirror_pdfs.py", "audit_opportunity_quality.py", "audit_pdf_integrity.py",
        ):
            self.assertIn(f'      - "{path}"', workflow)

    def test_daily_scrape_checks_out_latest_main_not_stale_push_sha(self):
        workflow = (ROOT / ".github" / "workflows" / "daily-scrape-and-publish.yml").read_text(encoding="utf-8")
        self.assertRegex(workflow, r"uses: actions/checkout@v4\\s+with:\\s+ref: main")

    def test_coverage_has_own_code_trigger_and_waits_for_daily_run(self):
        workflow = (ROOT / ".github" / "workflows" / "weekly-source-coverage.yml").read_text(encoding="utf-8")
        self.assertIn('workflows: ["Daily scrape and publish"]', workflow)
        self.assertIn('"audit_source_coverage.py"', workflow)
        self.assertIn('group: auditions-data-and-pages', workflow)


if __name__ == "__main__":
    unittest.main()
