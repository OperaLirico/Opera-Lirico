import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OfficialDocumentsPlacementTests(unittest.TestCase):
    def test_standalone_pdf_shelf_is_removed(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertNotIn('id="pdfs"', html)
        self.assertNotIn('data-open="pdfs"', html)
        self.assertNotIn("function renderPdfList()", app)
        self.assertNotIn("pdfSearchInput", app)

    def test_official_documents_are_attached_to_matching_institution_cards(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="conservatori"', html)
        self.assertIn('id="opera-academies"', html)
        self.assertIn('<span class="docs-key">对应官方文件</span>', app)
        self.assertIn("localPdfs(c)", app)
        self.assertIn("pickDocs(c.documents)", app)

    def test_old_year_pdf_links_are_not_shown_as_current_documents(self):
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("function currentDocs(list)", app)
        self.assertIn("Math.max(...years)>=2026", app)
        self.assertIn("return currentDocs(list);", app)
        self.assertIn("const docs=pickDocs(c.documents)", app)


if __name__ == "__main__":
    unittest.main()
