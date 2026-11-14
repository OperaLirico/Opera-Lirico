import unittest
from unittest.mock import patch

import system_health_check as health


class PublicSiteHealthTests(unittest.TestCase):
    def test_public_pages_accept_the_current_operalab_brand(self):
        responses = {
            "/": b"<!doctype html><title>OperaLab.</title>",
            "/masterclasses.html": b"<!doctype html><title>Masterclass | OperaLab.</title>",
            "/data/masterclasses.json": b'{"items":[]}',
            "/data/opportunities.json": b'{"items":[]}',
            "/data/conservatori.json": b'{"items":[]}',
        }

        def fake_fetch(url):
            path = url.removeprefix(health.BASE_URL)
            return responses[path]

        with patch.object(health, "fetch_url", side_effect=fake_fetch):
            checked = health.check_public_site(health.BASE_URL)

        self.assertEqual(checked, list(health.PUBLIC_PATHS))

    def test_old_internal_name_does_not_satisfy_public_homepage_brand_check(self):
        responses = {
            "/": b"<!doctype html><title>Opera Lirico</title>",
            "/masterclasses.html": b"<!doctype html><title>Masterclass | OperaLab.</title>",
            "/data/masterclasses.json": b'{"items":[]}',
            "/data/opportunities.json": b'{"items":[]}',
            "/data/conservatori.json": b'{"items":[]}',
        }

        def fake_fetch(url):
            path = url.removeprefix(health.BASE_URL)
            return responses[path]

        with patch.object(health, "fetch_url", side_effect=fake_fetch):
            with self.assertRaisesRegex(RuntimeError, "expected public brand OperaLab"):
                health.check_public_site(health.BASE_URL)


if __name__ == "__main__":
    unittest.main()
