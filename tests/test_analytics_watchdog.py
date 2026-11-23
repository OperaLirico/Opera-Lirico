import unittest
from datetime import date

from analytics_watchdog import assess_traffic_freshness


class AnalyticsWatchdogFreshnessTests(unittest.TestCase):
    def test_zero_last_48h_with_recent_data_is_warning_not_outage(self):
        problems, notes = assess_traffic_freshness(
            pageviews_7d=98,
            pageviews_last_48h=0,
            latest_date=date(2026, 11, 21),
            today=date(2026, 11, 23),
        )
        self.assertEqual(problems, [])
        self.assertEqual(len(notes), 1)
        self.assertIn("72 小时容忍窗口", notes[0])

    def test_data_older_than_72h_is_an_error(self):
        problems, notes = assess_traffic_freshness(
            pageviews_7d=98,
            pageviews_last_48h=0,
            latest_date=date(2026, 11, 20),
            today=date(2026, 11, 23),
        )
        self.assertEqual(len(problems), 2)
        self.assertEqual(notes, [])
        self.assertTrue(all("72 小时" in item for item in problems))

    def test_recent_pageviews_do_not_create_a_warning(self):
        problems, notes = assess_traffic_freshness(
            pageviews_7d=98,
            pageviews_last_48h=12,
            latest_date=date(2026, 11, 23),
            today=date(2026, 11, 23),
        )
        self.assertEqual(problems, [])
        self.assertEqual(notes, [])

    def test_small_traffic_does_not_trigger_high_volume_zero_window_rule(self):
        problems, notes = assess_traffic_freshness(
            pageviews_7d=8,
            pageviews_last_48h=0,
            latest_date=date(2026, 11, 20),
            today=date(2026, 11, 23),
        )
        self.assertEqual(problems, [])
        self.assertEqual(notes, [])


if __name__ == "__main__":
    unittest.main()
