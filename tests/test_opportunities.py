import json
import unittest

# Official application and PDF entry points were rechecked against publisher pages on 2026-11-10.
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "opportunities.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "data" / "opportunity.schema.json").read_text(encoding="utf-8"))
APP = (ROOT / "app.js").read_text(encoding="utf-8")
ALLOWED_TYPES = set(SCHEMA["properties"]["opportunity_type"]["enum"])
ALLOWED_VOICES = set(SCHEMA["properties"]["voice_types"]["items"]["enum"])


def parse_aware(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AssertionError(f"datetime must include timezone: {value}")
    return parsed


class OpportunityDataTests(unittest.TestCase):
    def test_dataset_shape_and_unique_ids(self):
        self.assertIsInstance(DATA, dict)
        self.assertIsInstance(DATA.get("items"), list)
        ids = [item.get("id") for item in DATA["items"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 1)

    def test_records_match_schema_contract(self):
        required = set(SCHEMA["required"])
        properties = set(SCHEMA["properties"])
        for item in DATA["items"]:
            with self.subTest(opportunity=item.get("id")):
                self.assertTrue(required.issubset(item))
                self.assertFalse(set(item) - properties, "unexpected schema properties")
                self.assertIn(item["opportunity_type"], ALLOWED_TYPES)
                self.assertIn(item["publisher_status"], {"official", "third_party", "unknown"})
                self.assertIn(item["review_status"], {"pending_manual_review", "verified", "rejected"})
                self.assertIn(item["publication_status"], {"draft", "published", "archived"})
                self.assertTrue(item["title"].strip())
                self.assertTrue(item["title_zh"].strip())
                self.assertTrue(item["source_name"].strip())
                self.assertTrue(item["evidence"])

    def test_published_records_must_be_verified_official(self):
        for item in DATA["items"]:
            if item["publication_status"] == "published":
                with self.subTest(opportunity=item["id"]):
                    self.assertEqual(item["review_status"], "verified")
                    self.assertEqual(item["publisher_status"], "official")

    def test_all_published_records_have_first_party_evidence(self):
        for item in DATA["items"]:
            if item["publication_status"] != "published":
                continue
            evidence_urls = {e["url"] for e in item["evidence"]}
            with self.subTest(opportunity=item["id"]):
                self.assertTrue(
                    item["announcement_url"] in evidence_urls
                    or item.get("official_pdf_url") in evidence_urls
                )
                for evidence in item["evidence"]:
                    self.assertTrue(evidence["excerpt"].strip())
                    self.assertTrue(evidence["url"].startswith("https://"))

    def test_dates_are_timezone_aware_and_chronological(self):
        for item in DATA["items"]:
            checked = parse_aware(item["checked_at"])
            if item.get("last_verified_at"):
                self.assertLessEqual(checked, parse_aware(item["last_verified_at"]))
            deadline = item.get("application_deadline_at")
            if deadline:
                self.assertGreater(parse_aware(deadline), checked)
            opened = item.get("application_open_at")
            if opened and deadline:
                self.assertLessEqual(parse_aware(opened), parse_aware(deadline))
            audition = item.get("audition_start_at")
            if audition and deadline:
                self.assertLess(parse_aware(deadline), parse_aware(audition))
            end = item.get("audition_end_at")
            if audition and end:
                self.assertLessEqual(parse_aware(audition), parse_aware(end))

    def test_urls_and_voice_types_are_valid(self):
        url_fields = ("source_url", "announcement_url", "application_url", "official_pdf_url")
        for item in DATA["items"]:
            with self.subTest(opportunity=item["id"]):
                for field in url_fields:
                    if item.get(field):
                        parsed = urlparse(item[field])
                        self.assertEqual(parsed.scheme, "https")
                        self.assertTrue(parsed.netloc)
                for voice in item.get("voice_types", []):
                    self.assertIn(voice, ALLOWED_VOICES)
                if "fee_eur" in item:
                    self.assertGreaterEqual(item["fee_eur"], 0)

    def test_frontend_loads_structured_data_and_applies_publication_gate(self):
        self.assertIn("data/opportunities.json", APP)
        self.assertIn("record.publication_status!=='published'", APP)
        self.assertIn("record.review_status!=='verified'", APP)
        self.assertIn("record.publisher_status!=='official'", APP)
        self.assertIn("Date.parse(deadline)<Date.now()", APP)

    def test_chinese_titles_and_full_section_search_are_wired(self):
        self.assertIn("record.title_zh||record.title", APP)
        self.assertIn("o.originalTitle", APP)
        self.assertIn("c.requirements||[]", APP)
        self.assertIn("pdfSearchInput", APP)
        self.assertIn("filteredRows", APP)

    def test_opportunity_cards_show_notes_and_official_pdf_links(self):
        self.assertIn("record.notes", APP)
        self.assertIn("officialPdfUrl:record.official_pdf_url", APP)
        self.assertIn("o.officialPdfUrl", APP)
        self.assertIn("下载官方简章 PDF", APP)

    def test_teatro_massimo_contralto_exam_date_conflict_is_not_silently_published(self):
        record = next(item for item in DATA["items"]
                      if item["id"] == "teatro-massimo-2-contralti-2026")
        self.assertEqual(record["publication_status"], "published")
        self.assertEqual(record["review_status"], "verified")
        self.assertNotIn("audition_start_at", record)
        self.assertIn("12月19日", record["notes"])
        self.assertIn("12月20日", record["notes"])
        self.assertTrue(record["official_pdf_url"].endswith("BandoSelezione_2Contralti_TM_2026.pdf"))

    def test_published_records_have_an_application_or_official_pdf_link(self):
        for item in DATA.get("items", []):
            if item.get("publication_status") == "published":
                with self.subTest(opportunity=item.get("id")):
                    self.assertTrue(item.get("application_url") or item.get("official_pdf_url"))

    def test_application_and_pdf_links_are_https(self):
        for item in DATA.get("items", []):
            for field in ("application_url", "official_pdf_url"):
                value = item.get(field)
                if value:
                    with self.subTest(opportunity=item.get("id"), field=field):
                        self.assertTrue(value.startswith("https://"))



if __name__ == "__main__":
    unittest.main()
