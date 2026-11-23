import unittest
from unittest import mock

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

    def test_source_fetch_url_preserves_tls_belli_publisher_hostname(self):
        url = "https://www.tls-belli.it/bandi_e_avvisi/?x=1"
        self.assertEqual(audit.source_fetch_url(url), url)

    def test_inventory_hash_tracks_publisher_url_exactly(self):
        www = [{"source_id": "source-10", "url": "https://www.tls-belli.it/bandi_e_avvisi/", "kind": "registered"}]
        apex = [{"source_id": "source-10", "url": "https://tls-belli.it/bandi_e_avvisi/", "kind": "registered"}]
        self.assertNotEqual(audit.inventory_hash(www), audit.inventory_hash(apex))

    def test_tls_belli_scan_uses_verified_stdlib_transport(self):
        source = {
            "source_id": "source-10",
            "name": "Teatro Lirico Sperimentale di Spoleto",
            "url": "https://www.tls-belli.it/bandi_e_avvisi/",
            "kind": "registered",
            "review_status": "auto_approved_official",
            "publisher_status": "official",
            "relevance_status": "relevant",
            "audit_confidence": "high",
        }
        with mock.patch.object(
            audit, "fetch_tls_belli_page",
            return_value=(200, "Bandi e avvisi", "Concorso internazionale di canto per giovani cantanti lirici"),
        ) as fallback, mock.patch.object(audit.Fetcher, "get") as scrapling_get:
            result = audit.scan_one(source, None, "2026-11-23T00:00:00+00:00")
        fallback.assert_called_once_with(source["url"])
        scrapling_get.assert_not_called()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["http_status"], 200)
        self.assertTrue(result["vocal_signal"])

    def test_source_fetch_url_does_not_rewrite_other_hosts(self):
        url = "https://www.example.org/path"
        self.assertEqual(audit.source_fetch_url(url), url)

    def test_canonical_url_drops_fragment_only(self):
        self.assertEqual(
            audit.canonical_url("HTTPS://Example.org/a?x=1#section"),
            "https://example.org/a?x=1",
        )

    def test_initial_baseline_does_not_claim_change_detection(self):
        state = {
            "cycle": "2026-W46", "started_at": "now", "updated_at": "now",
            "scan_status": "completed", "inventory_count": 1,
            "completed_source_ids": ["source-1"], "results": {},
            "inventory_sha256": "abc", "previous_cycle_complete": False,
        }
        report = audit.render_report(state)
        self.assertIn("first baseline", report)
        self.assertIn("cannot be compared until a later complete weekly scan", report)

    def test_complete_prior_cycle_enables_change_comparison(self):
        state = {
            "cycle": "2026-W47", "started_at": "now", "updated_at": "now",
            "scan_status": "completed", "inventory_count": 1,
            "completed_source_ids": ["source-1"], "results": {},
            "inventory_sha256": "abc", "previous_cycle_complete": True,
        }
        report = audit.render_report(state)
        self.assertIn("Changed normalized text hashes: 0", report)

    def test_inventory_is_unique_and_does_not_double_count_extra_registry(self):
        inventory = audit.source_inventory()
        ids = [item["source_id"] for item in inventory]
        urls = [audit.canonical_url(item["url"]) for item in inventory]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(urls), len(set(urls)))
        self.assertTrue(all(item["kind"] in {"registered", "pending_candidate"} for item in inventory))


if __name__ == "__main__":
    unittest.main()
