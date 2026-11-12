import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "masterclasses.html").read_text(encoding="utf-8")


class MasterclassUnderlineTests(unittest.TestCase):
    def test_page_uses_versioned_stylesheet_and_scoped_page_class(self):
        self.assertIn('styles.css?v=ux17', PAGE)
        self.assertIn('<body class="master-page">', PAGE)

    def test_all_masterclass_page_text_and_link_states_disable_underlines(self):
        self.assertIn('.master-page,.master-page *', PAGE)
        self.assertIn('-webkit-text-decoration:none!important', PAGE)
        self.assertIn('text-decoration-line:none!important', PAGE)
        self.assertIn('a:-webkit-any-link', PAGE)
        self.assertIn('border-bottom:0!important', PAGE)


if __name__ == "__main__":
    unittest.main()
