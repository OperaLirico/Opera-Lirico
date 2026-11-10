import unittest
from unittest.mock import patch

import audit_extraction_pilot as pilot
from audit_extraction_pilot import (
    feed_summary, metrics, parse_sitemap, robots_allows, permitted_fetch,
)


class ExtractionPilotHelperTests(unittest.TestCase):
    def test_robots_wildcards_and_specific_allow_precedence(self):
        robots = """User-agent: *
Disallow: /private*
Allow: /private/open$
"""
        self.assertFalse(robots_allows("https://example.org/private/secret", robots))
        self.assertTrue(robots_allows("https://example.org/private/open", robots))
        self.assertTrue(robots_allows("https://example.org/public", robots))

    def test_sitemap_index_returns_type_and_locations(self):
        xml = b"""<?xml version="1.0"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <sitemap><loc>https://example.org/auditions-sitemap.xml</loc></sitemap>
        </sitemapindex>"""
        result = parse_sitemap(xml)
        self.assertEqual(result["kind"], "sitemapindex")
        self.assertEqual(result["locs"], ["https://example.org/auditions-sitemap.xml"])

    def test_feed_summary_counts_vocal_entries_not_all_entries(self):
        xml = b"""<rss version="2.0"><channel>
          <item><title>Audizioni per tenore</title><description>Concorso lirico</description></item>
          <item><title>Nuovo calendario concerti</title><description>Stagione sinfonica</description></item>
        </channel></rss>"""
        result = feed_summary(xml)
        self.assertEqual(result["entry_count"], 2)
        self.assertEqual(result["relevant_entry_count"], 1)
        self.assertEqual(result["relevant_titles"], ["Audizioni per tenore"])

    def test_cross_host_redirect_checks_destination_robots_before_fetch(self):
        source_policy = {"status": "ok", "http_status": 200, "body": b"User-agent: *\nAllow: /"}
        target_policy = {"status": "ok", "http_status": 200, "body": b"User-agent: *\nDisallow: /private"}
        redirect = {"status": "redirect_requires_policy_check", "http_status": 302,
                    "redirect_url": "https://cdn.example.org/private/page", "body": b""}
        with (
            patch.object(pilot, "request_bytes", return_value=redirect) as request,
            patch.object(pilot, "fetch_robots", return_value=target_policy),
        ):
            result = permitted_fetch("https://example.org/page", "https://example.org/page", source_policy)
        self.assertEqual(result["status"], "robots_disallowed")
        self.assertEqual(request.call_count, 1)

    def test_cross_host_redirect_stops_when_destination_robots_unavailable(self):
        source_policy = {"status": "ok", "http_status": 200, "body": b"User-agent: *\nAllow: /"}
        redirect = {"status": "redirect_requires_policy_check", "http_status": 301,
                    "redirect_url": "https://other.example.org/page", "body": b""}
        unavailable = {"status": "http_error", "http_status": 503, "body": b""}
        with (
            patch.object(pilot, "request_bytes", return_value=redirect) as request,
            patch.object(pilot, "fetch_robots", return_value=unavailable),
        ):
            result = permitted_fetch("https://example.org/page", "https://example.org/page", source_policy)
        self.assertEqual(result["status"], "robots_unavailable")
        self.assertEqual(request.call_count, 1)

    def test_same_host_redirect_rechecks_destination_path_robots(self):
        source_policy = {
            "status": "ok", "http_status": 200,
            "body": b"User-agent: *\nAllow: /public\nDisallow: /private",
        }
        redirect = {"status": "redirect_requires_policy_check", "http_status": 302,
                    "redirect_url": "https://example.org/private/page", "body": b""}
        with patch.object(pilot, "request_bytes", return_value=redirect) as request:
            result = permitted_fetch("https://example.org/public/page",
                                     "https://example.org/public/page", source_policy)
        self.assertEqual(result["status"], "robots_disallowed")
        self.assertEqual(request.call_count, 1)

    def test_same_host_redirect_follows_after_destination_path_is_allowed(self):
        source_policy = {"status": "ok", "http_status": 200, "body": b"User-agent: *\nAllow: /"}
        redirect = {"status": "redirect_requires_policy_check", "http_status": 301,
                    "redirect_url": "https://example.org/canonical/page", "body": b""}
        final = {"status": "ok", "http_status": 200, "body": b"ok",
                 "final_url": "https://example.org/canonical/page"}
        with patch.object(pilot, "request_bytes", side_effect=[redirect, final]) as request:
            result = permitted_fetch("https://example.org/page", "https://example.org/page", source_policy)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(request.call_count, 2)

    def test_metrics_separates_link_label_from_href_retention(self):
        anchors = [
            {"text": "Scarica il bando", "url": "https://example.org/bando.pdf"},
            {"text": "Domanda di iscrizione", "url": "https://example.org/apply"},
        ]
        result = metrics("Scarica il bando. Il termine è il 30 novembre.", anchors)
        self.assertEqual(result["relevant_dom_link_labels_available"], 2)
        self.assertEqual(result["relevant_dom_link_labels_retained_in_text"], 1)
        self.assertEqual(result["relevant_link_targets_available"], 2)
        self.assertEqual(result["relevant_link_targets_retained_in_text"], 0)


if __name__ == "__main__":
    unittest.main()
