import unittest

import audit_source_coverage as audit


class SourceCoverageTests(unittest.TestCase):
    def test_inventory_hash_is_stable_and_sensitive_to_changes(self):
        items = [
            {"source_id": "source-1", "url": "https://example.org/a", "kind": "registered"},
            {"source_id": "source-2", "url": "https://example.org/b", "kind": "registered"},
        ]
        self.assertEqual(audit.inventory_hash(items), audit.inventory_hash(items))
        self.assertNotEqual(
            audit.inventory_hash(items),
            audit.inventory_hash(items + [{"source_id": "source-3", "url": "https://example.org/c", "kind": "registered"}]),
        )

    def test_canonical_url_drops_fragment_only(self):
        self.assertEqual(
            audit.canonical_url("HTTPS://Example.org/a?x=1#section"),
            "https://example.org/a?x=1",
        )

    def test_inventory_is_unique_and_does_not_double_count_extra_registry(self):
        inventory = audit.source_inventory()
        ids = [item["source_id"] for item in inventory]
        urls = [audit.canonical_url(item["url"]) for item in inventory]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(urls), len(set(urls)))
        self.assertTrue(all(item["kind"] in {"registered", "pending_candidate"} for item in inventory))


if __name__ == "__main__":
    unittest.main()
