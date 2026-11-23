import unittest

from discover_europe_institutions import (
    EUROPEAN_COUNTRIES,
    member_cards,
    official_website,
)


class EuropeInstitutionDiscoveryTests(unittest.TestCase):
    def test_directory_parser_keeps_european_member_and_reads_city_and_status(self):
        page = b"""<html><body>
          <h2>Austria</h2>
          <div class="member-card">
            <p>Wien, Austria | Active members</p>
            <h3><a href="/member/mdw-vienna">mdw - University of Music and Performing Arts Vienna</a></h3>
          </div>
          <h2>Australia</h2>
          <div class="member-card">
            <p>Melbourne, Australia | Associate members</p>
            <h3><a href="/member/melbourne-music">University of Melbourne Music</a></h3>
          </div>
        </body></html>"""
        records = member_cards(page, "https://aec-music.eu/members/our-members")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["institution"], "mdw - University of Music and Performing Arts Vienna")
        self.assertEqual(records[0]["country"], "Austria")
        self.assertEqual(records[0]["city"], "Wien")
        self.assertEqual(records[0]["aec_membership"], "active_members")
        self.assertEqual(records[0]["id"], "mdw-vienna")

    def test_profile_parser_prefers_explicit_website_field(self):
        page = b"""<html><body>
          <li>Website <a href="https://www.mdw.ac.at/">www.mdw.ac.at</a></li>
          <a href="https://facebook.com/example">Facebook</a>
        </body></html>"""
        self.assertEqual(
            official_website(page, "https://aec-music.eu/member/mdw"),
            "https://www.mdw.ac.at/",
        )

    def test_profile_without_official_site_is_not_given_a_fabricated_url(self):
        page = b"""<html><body><p>Member details</p>
          <a href="https://facebook.com/example">Facebook</a>
        </body></html>"""
        self.assertIsNone(official_website(page, "https://aec-music.eu/member/example"))

    def test_european_allow_list_excludes_overseas_associate_members(self):
        self.assertIn("Austria", EUROPEAN_COUNTRIES)
        self.assertIn("United Kingdom", EUROPEAN_COUNTRIES)
        self.assertIn("Ukraine", EUROPEAN_COUNTRIES)
        self.assertNotIn("Australia", EUROPEAN_COUNTRIES)
        self.assertNotIn("United States", EUROPEAN_COUNTRIES)


if __name__ == "__main__":
    unittest.main()
