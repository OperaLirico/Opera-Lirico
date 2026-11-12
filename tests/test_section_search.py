import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")


class SectionSearchTests(unittest.TestCase):
    def test_repertoire_voice_filter_is_connected(self):
        self.assertIn('id="musicVoiceFilter"', INDEX)
        self.assertIn("function matchesVoiceFilter", APP)
        self.assertIn("visibleRepertoire=repertoire.filter", APP)
        self.assertIn("musicVoiceFilter.addEventListener('change'", APP)
        for voice in ("tenor", "soprano", "mezzo", "baritone", "bass", "contralto"):
            self.assertIn(voice, APP)

    def test_conservatory_search_covers_requirements_and_deadlines(self):
        self.assertIn("c.requirements||[]", APP)
        self.assertIn("c.deadline_lines||[]", APP)
        self.assertIn("c.exam_dates||[]", APP)

    def test_pdf_shelf_has_a_search_control_and_filter(self):
        self.assertIn('id="pdfSearchInput"', INDEX)
        self.assertIn("filteredRows", APP)
        self.assertIn("pdfSearch.addEventListener('input',renderPdfList)", APP)

    def test_new_search_controls_have_styles(self):
        self.assertIn(".music-voice-filter", CSS)
        self.assertIn(".pdf-toolbar", CSS)


if __name__ == "__main__":
    unittest.main()
