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
                        "assessed_keep_scrapling_with_feed_discovery",
                        "assessed_keep_scrapling_html_only",
                    })
                    self.assertTrue(entry["alternatives_assessed"])
                    self.assertTrue(entry.get("last_assessed_at"))
                    report_path = entry.get("evidence_report", "")
                    self.assertTrue(report_path.startswith("reports/p2/"))
                    self.assertTrue((ROOT / report_path).exists())

    def test_first_four_pilot_batches_have_evidence_backed_strategy_assessments(self):
        policy = json.loads((ROOT / "data" / "source_fetch_policies.json").read_text(encoding="utf-8"))
        assessed = {item["source_id"]: item for item in policy["entries"]
                    if item["strategy_status"] != "baseline_only"}
        self.assertEqual(set(assessed), {
            "source-1", "source-2", "source-3", "source-9", "source-15",
            "source-4", "source-5", "source-6", "source-16", "source-17",
            "source-7", "source-8", "source-10", "source-18", "source-20",
            "source-12", "source-13", "source-14", "source-21", "source-22",
        })
        for source_id, item in assessed.items():
            with self.subTest(source_id=source_id):
                self.assertEqual(item["current_fetch_method"], "scrapling")
                self.assertTrue(item["alternatives_assessed"])
                self.assertTrue(item["discovery_methods"])
                batch_date = item["assessment_batch"].split("-", 2)[-1]
                self.assertIn(batch_date, item["last_assessed_at"])
                self.assertIn(batch_date, item["assessment_note"])
                self.assertIn(item.get("assessment_batch"), {
                    "batch-1-2026-11-10", "batch-2-2026-11-10",
                    "batch-3-2026-11-10", "batch-4-2026-11-12",
                })
                self.assertTrue((ROOT / item["evidence_report"]).exists())
                self.assertTrue(item["evidence_report"].startswith("reports/p2/"))

        for batch, batch_date in (
            (1, "2026-11-10"), (2, "2026-11-10"),
            (3, "2026-11-10"), (4, "2026-11-12"),
        ):
            stem = f"source-strategy-batch-{batch}-{batch_date}"
            self.assertTrue((ROOT / "reports" / "p2" / f"{stem}.json").exists())
            self.assertTrue((ROOT / "reports" / "p2" / f"{stem}.md").exists())

    def test_batch_four_uses_the_advertised_rss_feed_only_for_source_13(self):
        policy = json.loads((ROOT / "data" / "source_fetch_policies.json").read_text(encoding="utf-8"))
        source = next(item for item in policy["entries"] if item["source_id"] == "source-13")
        self.assertEqual(source["strategy_status"], "assessed_keep_scrapling_with_feed_discovery")
        self.assertIn("rss_atom", source["discovery_methods"])
        self.assertEqual(source["current_fetch_method"], "scrapling")
        self.assertFalse(any("production" in x.lower() and "switch" in x.lower() for x in source.get("discovery_methods", [])))

    def test_coverage_inventory_joins_source_review_classification(self):
        from audit_source_coverage import source_inventory
        inventory = [item for item in source_inventory() if item["kind"] == "registered"]
        counts = {}
        for item in inventory:
            counts[item["review_status"]] = counts.get(item["review_status"], 0) + 1
        self.assertEqual(len(inventory), 44)
        self.assertEqual(counts.get("auto_approved_official"), 26)
        self.assertEqual(counts.get("auto_approved_third_party"), 4)
        self.assertEqual(counts.get("needs_review"), 10)
        self.assertEqual(counts.get("irrelevant_candidate"), 3)
        self.assertEqual(counts.get("duplicate_candidate"), 1)
        self.assertEqual(sum(counts.values()), 44)
        self.assertNotIn("legacy_unreviewed", counts)
        self.assertNotIn("classification_missing", counts)

    def test_current_source_audit_overrides_baseline_classification(self):
        from audit_source_coverage import source_inventory
        registered = {
            item["source_id"]: item
            for item in source_inventory()
            if item["kind"] == "registered"
        }
        self.assertEqual(registered["source-97"]["review_status"], "needs_review")
        self.assertEqual(registered["source-98"]["review_status"], "needs_review")
        self.assertEqual(registered["source-100"]["review_status"], "needs_review")
        self.assertEqual(registered["source-101"]["review_status"], "auto_approved_third_party")
        self.assertEqual(registered["source-102"]["review_status"], "duplicate_candidate")
        self.assertEqual(registered["source-100"]["audit_confidence"], "low")
        self.assertEqual(registered["source-97"]["audit_date"], "2026-11-12")
        self.assertTrue(registered["source-97"]["audit_evidence_url"])

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
                if item.get("publisher_status") == "official":
                    self.assertEqual(item.get("auto_review_status"), "auto_approved_official")
                    self.assertEqual(item.get("confidence"), "high")
                    self.assertFalse(item.get("production_activation", False))


    def test_auto_reviewed_third_party_candidate_stays_out_of_production_registry(self):
        candidates = json.loads((ROOT / "data" / "source_candidates.json").read_text(encoding="utf-8"))
        candidate = next(item for item in candidates["items"] if item["candidate_id"] == 1)
        self.assertEqual(candidate["review_status"], "pending_manual_review")
        self.assertEqual(candidate["auto_review_status"], "auto_approved_third_party")
        self.assertEqual(candidate["publisher_status"], "third_party")
        self.assertEqual(candidate["relevance_status"], "relevant")
        self.assertEqual(candidate["confidence"], "high")

        sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
        policies = json.loads((ROOT / "data" / "source_fetch_policies.json").read_text(encoding="utf-8"))
        self.assertNotIn(candidate["url"], {item["url"] for item in sources})
        self.assertNotIn(candidate["url"], {item["url"] for item in policies["entries"]})

        from audit_source_coverage import source_inventory
        audited = next(item for item in source_inventory() if item["source_id"] == "candidate-1")
        self.assertEqual(audited["kind"], "pending_candidate")
        self.assertEqual(audited["review_status"], "auto_approved_third_party")
        self.assertEqual(audited["publisher_status"], "third_party")
        self.assertEqual(audited["audit_confidence"], "high")

    def test_auto_approved_official_candidate_stays_out_of_production_registry(self):
        candidates = json.loads((ROOT / "data" / "source_candidates.json").read_text(encoding="utf-8"))
        candidate = next(item for item in candidates["items"] if item["candidate_id"] == 2)
        self.assertEqual(candidate["review_status"], "pending_manual_review")
        self.assertEqual(candidate["auto_review_status"], "auto_approved_official")
        self.assertEqual(candidate["publisher_status"], "official")
        self.assertEqual(candidate["relevance_status"], "relevant")
        self.assertEqual(candidate["confidence"], "high")
        self.assertFalse(candidate["production_activation"])
        self.assertEqual(candidate["access_policy_status"], "not_independently_verified_for_child_path")

        sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
        policies = json.loads((ROOT / "data" / "source_fetch_policies.json").read_text(encoding="utf-8"))
        self.assertNotIn(candidate["url"], {item["url"] for item in sources})
        self.assertNotIn(candidate["url"], {item["url"] for item in policies["entries"]})

        from audit_source_coverage import source_inventory
        audited = next(item for item in source_inventory() if item["source_id"] == "candidate-2")
        self.assertEqual(audited["review_status"], "auto_approved_official")
        self.assertEqual(audited["publisher_status"], "official")
        self.assertEqual(audited["audit_confidence"], "high")

if __name__ == "__main__":
    unittest.main()
