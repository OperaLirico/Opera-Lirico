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


if __name__ == "__main__":
    unittest.main()
