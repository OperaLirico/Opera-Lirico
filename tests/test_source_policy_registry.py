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
                self.assertEqual(entry["strategy_status"], "baseline_only")
                self.assertFalse(entry["alternatives_assessed"])

    def test_coverage_inventory_joins_source_review_classification(self):
        from audit_source_coverage import source_inventory
        inventory = [item for item in source_inventory() if item["kind"] == "registered"]
        counts = {}
        for item in inventory:
            counts[item["review_status"]] = counts.get(item["review_status"], 0) + 1
        self.assertEqual(len(inventory), 44)
        self.assertEqual(counts.get("auto_approved_official"), 26)
        self.assertEqual(counts.get("auto_approved_third_party"), 4)
        self.assertEqual(counts.get("needs_review"), 2)
        self.assertEqual(counts.get("irrelevant_candidate"), 12)
        self.assertNotIn("legacy_unreviewed", counts)

    def test_candidate_queue_stays_separate_and_pending(self):
        candidates_path = ROOT / "data" / "source_candidates.json"
        candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
        for item in candidates.get("items", []):
            with self.subTest(candidate=item.get("candidate_id")):
                self.assertEqual(item.get("review_status"), "pending_manual_review")
                self.assertNotEqual(item.get("publisher_status"), "official")


if __name__ == "__main__":
    unittest.main()
