import json
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
        self.assertRegex(workflow, r"uses: actions/checkout@(?:v5|[0-9a-f]{40})(?: # v5)?\s+with:\s+ref: main")

    def test_p2_pilot_only_reruns_for_pilot_code_or_dependency_changes(self):
        workflow = (ROOT / ".github" / "workflows" / "p2-p4-extraction-pilot.yml").read_text(encoding="utf-8")
        self.assertIn('"audit_extraction_pilot.py"', workflow)
        self.assertIn('"requirements.txt"', workflow)
        self.assertNotIn('"data/source_fetch_policies.json"', workflow)
        self.assertNotIn('"reports/source-audit-baseline-2026-11-10.json"', workflow)
        self.assertNotIn('".github/workflows/p2-p4-extraction-pilot.yml"', workflow)


    def test_system_health_runs_on_schedule_not_every_upstream_completion(self):
        workflow = (ROOT / ".github" / "workflows" / "system-health-check.yml").read_text(encoding="utf-8")
        self.assertIn("  schedule:", workflow)
        self.assertIn("  workflow_dispatch:", workflow)
        self.assertNotIn("  workflow_run:", workflow)
        self.assertNotIn("github.event.workflow_run", workflow)

    def test_failure_alert_only_listens_to_operationally_critical_workflows(self):
        # The digest is scheduled (it scans the last 24h instead of firing on every
        # completion), but it must still report only the workflows whose failure
        # actually blocks production. Noisy jobs are filtered out by name.
        workflow = (ROOT / ".github" / "workflows" / "workflow-failure-alert.yml").read_text(encoding="utf-8")
        self.assertIn("  schedule:", workflow)
        for name in (
            "Daily source refresh", "Deploy GitHub Pages",
            "Deploy private operations dashboard", "Discover masterclasses",
            "Source quality tests", "System health check", "KV backup",
        ):
            self.assertIn(f'"{name}"', workflow)
        for name in ("Generate social content drafts", "Weekly email digest (draft only)", "Weekly source coverage", "Weekly source discovery", "P2 P4 extraction pilot"):
            self.assertNotIn(f'"{name}"', workflow)

    def test_coverage_has_own_code_trigger_and_waits_for_daily_run(self):
        workflow = (ROOT / ".github" / "workflows" / "weekly-source-coverage.yml").read_text(encoding="utf-8")
        self.assertIn('workflows: ["Daily source refresh"]', workflow)
        self.assertIn('"audit_source_coverage.py"', workflow)
        self.assertIn('group: weekly-source-coverage', workflow)


    def test_rea_upstream_watch_tracks_official_upstream_and_mcp_contracts(self):
        workflow = (ROOT / ".github" / "workflows" / "rea-upstream-watch.yml").read_text(encoding="utf-8")
        self.assertIn('const upstream = { owner: "morluto", repo: "rea" };', workflow)
        self.assertIn('github.rest.repos.getCommit({ ...upstream, ref: "main" })', workflow)
        self.assertIn('github.rest.repos.listTags({ ...upstream, per_page: 100 })', workflow)
        for path in (
            ".agents/skills/reverse-engineer-anything/SKILL.md",
            "docs/getting-started/installation.md",
            ".agents/skills/reverse-engineer-anything/references/connection-and-recovery.md",
            "docs/reference/mcp-contracts.md",
            "install.sh",
            "package.json",
        ):
            self.assertIn(path, workflow)
        self.assertIn("baseline.upstream_main_commit", workflow)
        self.assertIn("mcp_contracts_blob_sha", workflow)
        self.assertNotIn('path: ".agents/skills/rea-reverse-engineering/SKILL.md"', workflow)

    def test_rea_upstream_watch_parses_nested_skill_metadata(self):
        workflow = (ROOT / ".github" / "workflows" / "rea-upstream-watch.yml").read_text(encoding="utf-8")
        self.assertIn("const metadataBlock = upstreamSkillText.match(", workflow)
        self.assertIn("const metadataMatch = metadataBlock.match(", workflow)
    def test_rea_skill_baseline_matches_reviewed_upstream_commit(self):
        baseline = json.loads(
            (ROOT / ".agents" / "skills" / "rea-reverse-engineering" / "references" / "upstream-baseline.json")
            .read_text(encoding="utf-8")
        )
        skill = (ROOT / ".agents" / "skills" / "rea-reverse-engineering" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(baseline["upstream_main_commit"], skill)
        self.assertIn(baseline["release_tag"], skill)
        self.assertIn(baseline["skill_metadata_version"], skill)


if __name__ == "__main__":
    unittest.main()
