import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import robots_policy


class RobotsPolicyTests(unittest.TestCase):
    def test_robots_wildcards_and_allow_precedence(self):
        rules = """User-agent: *
Disallow: /private*
Allow: /private/open$
"""
        self.assertFalse(robots_policy.robots_allows("https://example.org/private/secret", rules))
        self.assertTrue(robots_policy.robots_allows("https://example.org/private/open", rules))
        self.assertTrue(robots_policy.robots_allows("https://example.org/public", rules))

    def test_404_robots_file_allows_but_unavailable_policy_fails_closed(self):
        with patch.object(robots_policy, "fetch_robots", return_value={
            "status": "not_found", "http_status": 404, "robots_url": "https://example.org/robots.txt"
        }):
            self.assertTrue(robots_policy.check_url("https://example.org/open")["allowed"])
        with patch.object(robots_policy, "fetch_robots", return_value={
            "status": "unavailable", "http_status": 503, "robots_url": "https://example.org/robots.txt"
        }):
            self.assertFalse(robots_policy.check_url("https://example.org/open")["allowed"])

    def test_disallowed_path_is_not_requested(self):
        response = SimpleNamespace(status=200, headers={})
        fetcher = Mock(return_value=response)
        with patch.object(robots_policy, "check_url", return_value={
            "allowed": False, "status": "robots_disallowed"
        }):
            page, decision = robots_policy.fetch_page_with_robots(
                "https://example.org/private", fetcher, delay=0
            )
        self.assertIsNone(page)
        self.assertEqual(decision["status"], "robots_disallowed")
        fetcher.assert_not_called()

    def test_cross_host_redirect_checks_destination_before_following(self):
        redirect = SimpleNamespace(status=302, headers={"Location": "https://cdn.example.org/file"})
        final = SimpleNamespace(status=200, headers={})
        fetcher = unittest.mock.Mock(side_effect=[redirect, final])
        checks = [
            {"allowed": True, "status": "allowed", "robots_status": "ok"},
            {"allowed": False, "status": "robots_disallowed", "robots_status": "ok"},
        ]
        with patch.object(robots_policy, "check_url", side_effect=checks) as check:
            page, decision = robots_policy.fetch_page_with_robots(
                "https://example.org/file", fetcher, delay=0
            )
        self.assertIsNone(page)
        self.assertEqual(decision["status"], "robots_disallowed")
        self.assertEqual(check.call_count, 2)
        self.assertEqual(fetcher.call_count, 1)
        self.assertFalse(fetcher.call_args.kwargs["follow_redirects"])
        self.assertFalse(fetcher.call_args.kwargs["stealthy_headers"])

    def test_cross_host_redirect_follows_only_when_destination_allows(self):
        redirect = SimpleNamespace(status=302, headers={"Location": "https://cdn.example.org/file"})
        final = SimpleNamespace(status=200, headers={})
        fetcher = unittest.mock.Mock(side_effect=[redirect, final])
        checks = [
            {"allowed": True, "status": "allowed", "robots_status": "ok"},
            {"allowed": True, "status": "allowed", "robots_status": "ok"},
        ]
        with patch.object(robots_policy, "check_url", side_effect=checks):
            page, decision = robots_policy.fetch_page_with_robots(
                "https://example.org/file", fetcher, delay=0
            )
        self.assertIs(page, final)
        self.assertEqual(decision["status"], "fetched")
        self.assertEqual(len(decision["redirect_chain"]), 1)
        self.assertEqual(fetcher.call_count, 2)


if __name__ == "__main__":
    unittest.main()
