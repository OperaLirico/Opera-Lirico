import json
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ROME = ZoneInfo("Europe/Rome")
DATA = json.loads((ROOT / "data" / "opportunities.json").read_text(encoding="utf-8"))
DATE_FIELDS = (
    "application_open_at", "application_deadline_at",
    "audition_start_at", "audition_end_at",
    "performance_start_at", "performance_end_at",
    "checked_at", "last_verified_at",
)


class OpportunityRomeTimezoneTests(unittest.TestCase):
    def test_all_recorded_datetimes_use_the_europe_rome_offset(self):
        for item in DATA.get("items", []):
            for field in DATE_FIELDS:
                value = item.get(field)
                if not value:
                    continue
                with self.subTest(opportunity=item.get("id"), field=field):
                    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    self.assertIsNotNone(parsed.tzinfo)
                    self.assertEqual(parsed.utcoffset(), parsed.astimezone(ROME).utcoffset())


if __name__ == "__main__":
    unittest.main()
