import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConservatoryTaxonomyTests(unittest.TestCase):
    def test_academies_and_choral_schools_have_explicit_types(self):
        data = json.loads((ROOT / "data/conservatori_manual.json").read_text(encoding="utf-8"))
        items = {item["number"]: item for item in data["items"]}
        self.assertEqual(items[303]["institution_type"], "choral_school")
        self.assertEqual(items[304]["institution_type"], "choral_school")
        self.assertEqual(sum(item["institution_type"] == "opera_academy" for item in items.values()), 9)
        self.assertEqual(sum(item["institution_type"] == "choral_school" for item in items.values()), 2)

    def test_frontend_renders_three_distinct_institution_groups(self):
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("title:'歌剧院专业学院'", app)
        self.assertIn("title:'合唱学校'", app)
        self.assertIn("title:'公立音乐学院'", app)
        self.assertIn("item.institution_type=note.institution_type", app)


if __name__ == "__main__":
    unittest.main()
