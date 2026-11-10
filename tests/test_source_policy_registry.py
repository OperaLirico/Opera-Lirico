import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SourceFetchPolicyRegistryTests(unittest.TestCase):
    def test_every_registered_source_has_one_baseline_policy(self):
        sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
        policy = json.loads((ROOT / "data" / "source_fetch_policies.json").read_text(encoding="utf-8"))
        by_url = {item["url"]: item for item in policy["entries"]}
        self.assertEqual(len(by_url), len(policy["entries"]))
        for source in sources:
            with self.subTest(source=source.get("source")):
                entry = by_url[source["url"]]
                self.assertEqual(entry["current_fetch_method"], "scrapling")
                if entry["strategy_status"] == "baseline_only":
                    self.assertFalse(entry["alternatives_assessed"])
                else:
                    self.assertIn(entry["strategy_status"], {
                        "assessed_keep_scrapling_with_sitemap_discovery",
                        "assessed_keep_scrapling_html_only",
                    })
                    self.assertTrue(entry["alternatives_assessed"])
                    self.assertTrue(entry.get("last_assessed_at"))
                    self.assertEqual(entry.get("evidence_report"), ".github/audits/extraction-pilot-latest.md")

    def test_first_pilot_batch_has_evidence_backed_strategy_assessments(self):
        policy = json.loads((ROOT / "data" / "source_fetch_policies.json").read_text(encoding="utf-8"))
        assessed = {item["source_id"]: item for item in policy["entries"]
                    if item["strategy_status"] != "baseline_only"}
        self.assertEqual(set(assessed), {
            "source-1", "source-2", "source-3", "source-9", "source-15",
            "source-4", "source-5", "source-6", "source-16", "source-17",
        })
        for source_id, item in assessed.items():
            with self.subTest(source_id=source_id):
                self.assertEqual(item["current_fetch_method"], "scrapling")
                self.assertTrue(item["alternatives_assessed"])
                self.assertTrue(item["discovery_methods"])
                self.assertIn("2026-11-10", item["last_assessed_at"])
                self.assertIn("2026-11-10", item["assessment_note"])
                self.assertIn(item.get("assessment_batch"), {
                    "batch-1-2026-11-10", "batch-2-2026-11-10"
                })
                self.assertTrue(item["evidence_report"].startswith("reports/p2/"))

    def test_coverage_inventory_joins_source_review_classification(self):
        from audit_source_coverage import source_inventory
        inventory = [item for item in source_inventory() if item["kind"] == "registered"]
        counts = {}
        for item in inventory:
            counts[item["review_status"]] = counts.get(item["review_status"], 0) + 1
        self.assertEqual(len(inventory), 44)
        self.assertEqual(counts.get("auto_approved_official"), 26)
        self.assertEqual(counts.get("auto_approved_third_party"), 4)
        self.assertEqual(counts.get("needs_review"), 1)
        self.assertEqual(counts.get("irrelevant_candidate"), 13)
        self.assertNotIn("legacy_unreviewed", counts)

    def test_source_audit_summary_matches_item_classifications(self):
        audit = json.loads((ROOT / "reports" / "source-audit-baseline-2026-11-10.json").read_text(encoding="utf-8"))
        actual = {}
        for item in audit["items"]:
            label = item["auto_review_status"]
            actual[label] = actual.get(label, 0) + 1
        self.assertEqual(audit["summary"]["classifications"], actual)

    def test_trafilatura_remains_evaluation_only(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        pilot_workflow = (ROOT / ".github" / "workflows" / "p2-p4-extraction-pilot.yml").read_text(encoding="utf-8")
        pilot_script = (ROOT / "audit_extraction_pilot.py").read_text(encoding="utf-8")
        self.assertNotIn("trafilatura", requirements.lower())
        self.assertIn("pip install trafilatura", pilot_workflow)
        self.assertIn("Selector(content=html_bytes", pilot_script)
        self.assertIn("trafilatura.extract", pilot_script)
        self.assertIn("production_changes", pilot_script)

    def test_candidate_queue_stays_separate_and_pending(self):
        candidates_path = ROOT / "data" / "source_candidates.json"
        candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
        for item in candidates.get("items", []):
            with self.subTest(candidate=item.get("candidate_id")):
                self.assertEqual(item.get("review_status"), "pending_manual_review")
                self.assertNotEqual(item.get("publisher_status"), "official")


if __name__ == "__main__":
    unittest.main()
