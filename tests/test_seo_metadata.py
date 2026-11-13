import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOME = (ROOT / "index.html").read_text(encoding="utf-8")
MASTER = (ROOT / "masterclasses.html").read_text(encoding="utf-8")


class SeoAndSharingTests(unittest.TestCase):
    def test_homepage_has_canonical_and_social_preview_metadata(self):
        self.assertIn('<title>OperaLab.｜意大利声乐机会、招生与曲目</title>', HOME)
        self.assertIn('property="og:site_name" content="OperaLab."', HOME)
        self.assertNotIn('Italia Audizioni', HOME)
        self.assertIn('rel="canonical" href="https://operalirico.github.io/Opera-Lirico/"', HOME)
        self.assertIn('property="og:image" content="https://operalirico.github.io/Opera-Lirico/og-image.png"', HOME)
        self.assertIn('name="twitter:card" content="summary_large_image"', HOME)
        self.assertIn('"@type": "WebSite"', HOME)

    def test_masterclass_page_has_page_specific_share_metadata(self):
        self.assertIn('<title>大师班与专业进修｜OperaLab.</title>', MASTER)
        self.assertIn('property="og:site_name" content="OperaLab."', MASTER)
        self.assertNotIn('Italia Audizioni', MASTER)
        self.assertIn('rel="canonical" href="https://operalirico.github.io/Opera-Lirico/masterclasses.html"', MASTER)
        self.assertIn('property="og:title" content="声乐大师班与专业进修｜OperaLab."', MASTER)
        self.assertIn('name="twitter:card" content="summary_large_image"', MASTER)

    def test_source_evidence_is_not_exposed_in_public_footer(self):
        self.assertNotIn('id="sourcesLink"', HOME)
        self.assertNotIn('id="sources-note"', HOME)
        self.assertNotIn('href="data/sources.json"', HOME)
        self.assertNotIn('href="data/conservatori.json"', HOME)

    def test_robots_points_to_the_project_sitemap(self):
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Allow: /", robots)
        self.assertIn("https://operalirico.github.io/Opera-Lirico/sitemap.xml", robots)

    def test_sitemap_contains_only_published_html_pages(self):
        tree = ET.parse(ROOT / "sitemap.xml")
        locs = [node.text for node in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(locs, [
            "https://operalirico.github.io/Opera-Lirico/",
            "https://operalirico.github.io/Opera-Lirico/masterclasses.html",
        ])


    def test_repertoire_quick_search_chips_are_unique(self):
        import re
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        chips = re.findall(r'class="search-chip" data-query="([^"]+)"', homepage)
        self.assertEqual(len(chips), len(set(chips)))
        self.assertEqual(len(chips), 12)

    def test_unreviewed_repertoire_archive_is_not_loaded_by_the_frontend(self):
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("repertoire_archive.json", app)

    def test_404_page_exists_and_returns_home_link(self):
        page = (ROOT / "404.html").read_text(encoding="utf-8")
        self.assertIn('name="robots" content="noindex,follow"', page)
        self.assertIn('href="./"', page)
        self.assertIn("ERROR 404", page)

    def test_share_image_source_has_expected_canvas(self):
        svg = ET.parse(ROOT / "og-image.png").getroot()
        self.assertEqual(svg.attrib.get("width"), "1200")
        self.assertEqual(svg.attrib.get("height"), "630")


if __name__ == "__main__":
    unittest.main()
