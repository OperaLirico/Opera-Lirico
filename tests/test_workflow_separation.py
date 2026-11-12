import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkflowSeparationTests(unittest.TestCase):
    def test_daily_source_refresh_does_not_run_for_frontend_or_opportunity_edits(self):
        workflow = (ROOT / ".github/workflows/daily-scrape-and-publish.yml").read_text(encoding="utf-8")
        self.assertIn("group: daily-source-refresh", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn('"data/sources.json"', workflow)
        self.assertIn('"scrape_sources.py"', workflow)
        self.assertNotIn('"app.js"', workflow)
        self.assertNotIn('"data/**"', workflow)
        self.assertIn("pages: write", workflow)
        self.assertIn("upload-pages-artifact", workflow)
        self.assertIn("group: github-pages-deploy", workflow)

    def test_pages_deploy_handles_site_content_without_running_scrapers(self):
        workflow = (ROOT / ".github/workflows/pages-deploy.yml").read_text(encoding="utf-8")
        self.assertIn('"app.js"', workflow)
        self.assertIn('"data/opportunities.json"', workflow)
        self.assertIn('"data/conservatori.json"', workflow)
        self.assertIn("group: github-pages-deploy", workflow)
        self.assertRegex(workflow, r"actions/deploy-pages@(?:v4|[0-9a-f]{40})(?: # v4)?")

    def test_weekly_coverage_has_independent_concurrency(self):
        workflow = (ROOT / ".github/workflows/weekly-source-coverage.yml").read_text(encoding="utf-8")
        self.assertIn("group: weekly-source-coverage-${{ github.event_name }}", workflow)
        self.assertNotIn("group: auditions-data-and-pages", workflow)

    def test_weekly_discovery_has_independent_concurrency(self):
        workflow = (ROOT / ".github/workflows/weekly-source-discovery.yml").read_text(encoding="utf-8")
        self.assertIn("group: weekly-source-discovery", workflow)
        self.assertNotIn("group: auditions-data-and-pages", workflow)


if __name__ == "__main__":
    unittest.main()
