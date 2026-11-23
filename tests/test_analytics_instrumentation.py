import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = (
    "index.html",
    "masterclasses.html",
    "voice-anatomy.html",
    "larynx-mechanism.html",
    "voice-lab.html",
    "privacy.html",
    "404.html",
)
BEACON = "https://static.cloudflareinsights.com/beacon.min.js"
TOKEN = "42879f330b824eb4843baa5bd13ba002"


class AnalyticsInstrumentationTests(unittest.TestCase):
    def test_every_public_html_page_loads_the_same_cloudflare_beacon(self):
        for page in PUBLIC_PAGES:
            with self.subTest(page=page):
                html = (ROOT / page).read_text(encoding="utf-8")
                self.assertIn(BEACON, html)
                self.assertIn(TOKEN, html)
                self.assertIn('type="module"', html)
                self.assertEqual(html.count(BEACON), 1)


if __name__ == "__main__":
    unittest.main()
