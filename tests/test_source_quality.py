import unittest

import grow_sources
import scrape_sources


class PreserveLastGoodTests(unittest.TestCase):
    def test_failed_refresh_keeps_previous_extract(self):
        previous = {
            "number": 1,
            "source": "Opera House",
            "url": "https://example.org/auditions",
            "status": "ok",
            "checked_at": "2026-11-09T10:00:00+01:00",
            "relevant_lines": ["Audizioni per cantanti lirici"],
            "relevant_links": [{"text": "Bando ufficiale", "url": "https://example.org/bando.pdf"}],
            "consecutive_failures": 0,
        }
        failed = {
            "number": 1,
            "source": "Opera House",
            "url": "https://example.org/auditions",
            "status": "http_error",
            "http_status": 403,
            "title": "",
            "relevant_lines": [],
            "relevant_links": [],
            "error": "HTTP 403",
        }
        result = scrape_sources.preserve_last_good(
            previous, failed, "2026-11-10T10:00:00+01:00"
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["relevant_lines"], previous["relevant_lines"])
        self.assertEqual(result["relevant_links"], previous["relevant_links"])
        self.assertTrue(result["stale"])
        self.assertEqual(result["last_attempt_http_status"], 403)
        self.assertEqual(result["consecutive_failures"], 1)
        self.assertEqual(result["checked_at"], previous["checked_at"])

    def test_extract_relevant_links_preserves_absolute_targets_and_excludes_noise(self):
        html = b"""<html><body>
          <a href="/uploads/2026/bando.pdf">Bando di selezione</a>
          <a href="https://example.org/application">Modulo domanda online</a>
          <a href="/privacy.pdf">Informativa privacy</a>
          <a href="javascript:void(0)">Audizioni</a>
          <a href="/uploads/2026/bando.pdf">Bando di selezione</a>
        </body></html>"""
        links, total, truncated = scrape_sources.extract_relevant_links(
            html, "https://example.org/audizioni/"
        )
        self.assertEqual(total, 2)
        self.assertFalse(truncated)
        self.assertEqual(
            {item["url"] for item in links},
            {"https://example.org/uploads/2026/bando.pdf", "https://example.org/application"},
        )

    def test_extract_relevant_links_uses_accessible_labels_for_icon_only_links(self):
        html = b"""<html><body>
          <a href="/apply/123" aria-label="Download audition application form" title="Official application"></a>
        </body></html>"""
        links, total, truncated = scrape_sources.extract_relevant_links(
            html, "https://example.org/audizioni/"
        )
        self.assertEqual(total, 1)
        self.assertFalse(truncated)
        self.assertEqual(links[0]["url"], "https://example.org/apply/123")
        self.assertEqual(links[0]["aria_label"], "Download audition application form")
        self.assertEqual(links[0]["title"], "Official application")

    def test_extract_relevant_links_classifies_documents_and_external_application_forms(self):
        html = b"""<html><body>
          <a href="/download/bando-2027.pdf" rel="noopener">Scarica il bando</a>
          <a href="//forms.example.net/apply/123" target="_blank"
             aria-label="Online application form"> </a>
          <a href="/audizioni/#details">Dettagli audizioni</a>
          <a href="/privacy.pdf">Informativa privacy</a>
        </body></html>"""
        links, total, truncated = scrape_sources.extract_relevant_links(
            html, "https://www.example.org/audizioni/"
        )
        by_type = {item["link_type"]: item for item in links}
        self.assertEqual(total, 3)
        self.assertFalse(truncated)
        self.assertIn("official_document", by_type)
        self.assertEqual(by_type["official_document"]["host"], "www.example.org")
        self.assertTrue(by_type["official_document"]["same_host"])
        self.assertEqual(by_type["official_document"]["rel"], "noopener")
        self.assertIn("application", by_type)
        self.assertEqual(by_type["application"]["host"], "forms.example.net")
        self.assertFalse(by_type["application"]["same_host"])
        self.assertEqual(
            by_type["application"]["aria_label"], "Online application form"
        )
        self.assertIn("notice", by_type)

    def test_extract_relevant_links_deduplicates_fragment_variants(self):
        html = b"""<html><body>
          <a href="/bando/2027.pdf#page=1">Bando ufficiale</a>
          <a href="/bando/2027.pdf#page=2">Bando ufficiale - seconda pagina</a>
        </body></html>"""
        links, total, truncated = scrape_sources.extract_relevant_links(
            html, "https://example.org/"
        )
        self.assertEqual(total, 1)
        self.assertFalse(truncated)
        self.assertEqual(len(links), 1)

    def test_extract_relevant_links_reports_truncation_instead_of_silently_dropping(self):
        html = ("<html><body>" + "".join(
            f'<a href="/bando-{i}.pdf">Bando {i}</a>' for i in range(1010)
        ) + "</body></html>").encode()
        links, total, truncated = scrape_sources.extract_relevant_links(html, "https://example.org/")
        self.assertEqual(total, 1010)
        self.assertEqual(len(links), 1000)
        self.assertTrue(truncated)

    def test_successful_refresh_replaces_snapshot_and_resets_failures(self):
        previous = {"status": "ok", "consecutive_failures": 3}
        current = {
            "number": 1,
            "status": "ok",
            "title": "New notice",
            "relevant_lines": ["Audizioni per tenori"],
        }
        result = scrape_sources.preserve_last_good(
            previous, current, "2026-11-10T10:00:00+01:00"
        )
        self.assertFalse(result["stale"])
        self.assertEqual(result["consecutive_failures"], 0)
        self.assertEqual(result["last_success_at"], "2026-11-10T10:00:00+01:00")

    def test_first_failure_is_recorded_without_inventing_snapshot(self):
        current = {"status": "error", "error": "timeout", "relevant_lines": []}
        result = scrape_sources.preserve_last_good(
            None, current, "2026-11-10T10:00:00+01:00"
        )
        self.assertTrue(result["stale"])
        self.assertEqual(result["last_attempt_status"], "error")
        self.assertEqual(result["relevant_lines"], [])

    def test_voice_related_audition_passes_to_review_queue(self):
        probe = {
            "status": "ok",
            "source": "Opera competition",
            "title": "International opera singing competition",
            "relevant_lines": [
                "Concorso internazionale di canto lirico",
                "Audizioni per soprano e tenore",
                "Application deadline 30 November 2026",
            ],
        }
        self.assertIsNone(
            grow_sources.candidate_rejection_reason(probe, "https://example.org/competition")
        )

    def test_instrument_only_audition_is_rejected(self):
        probe = {
            "status": "ok",
            "source": "Orchestra competition",
            "title": "Concorso 2026 - Primo Oboe",
            "relevant_lines": [
                "Concorso per primo oboe",
                "Audizione per strumentisti",
                "Prova finale il 15 dicembre 2026",
            ],
        }
        self.assertEqual(
            grow_sources.candidate_rejection_reason(probe, "https://example.org/oboe"),
            "non_vocal_role_only",
        )

    def test_actor_only_casting_is_rejected_even_on_an_opera_page(self):
        probe = {
            "status": "ok",
            "source": "Opera theatre",
            "title": "Audizioni per attori e attrici",
            "relevant_lines": [
                "Audizioni per attori e attrici per una nuova produzione",
                "Selezione per ruoli teatrali",
                "La produzione è realizzata da un teatro d'opera",
            ],
        }
        self.assertEqual(
            grow_sources.candidate_rejection_reason(probe, "https://example.org/auditions"),
            "non_vocal_role_only",
        )

    def test_instrument_notice_is_rejected_even_with_generic_opera_context(self):
        probe = {
            "status": "ok",
            "source": "Orchestra",
            "title": "Concorso per primo oboe",
            "relevant_lines": [
                "Audizione per primo oboe nell'orchestra del teatro d'opera",
                "La produzione operistica prevede prove orchestrali",
                "Domanda di partecipazione al concorso strumentale",
            ],
        }
        self.assertEqual(
            grow_sources.candidate_rejection_reason(probe, "https://example.org/oboe"),
            "non_vocal_role_only",
        )

    def test_legacy_irrelevant_sources_are_flagged_not_removed(self):
        item = {
            "source": "Orchestra competition",
            "title": "Concorso Primo Oboe",
            "status": "ok",
            "relevant_lines": ["Audizione per oboe", "Concorso strumentale"],
        }
        status, reason = grow_sources.legacy_relevance_status(item)
        self.assertEqual(status, "irrelevant_candidate")
        self.assertEqual(reason, "non_vocal_role_only")
        self.assertEqual(item["source"], "Orchestra competition")

    def test_legacy_vocal_source_still_requires_publisher_review(self):
        item = {
            "source": "Opera competition",
            "title": "Concorso internazionale di canto",
            "status": "ok",
            "relevant_lines": ["Audizioni per soprano e tenore"],
        }
        status, reason = grow_sources.legacy_relevance_status(item)
        self.assertEqual(status, "needs_review")
        self.assertEqual(reason, "vocal_signal_found_but_publisher_not_verified")

    def test_review_labels_survive_successful_refresh(self):
        previous = {
            "review_status": "legacy_unreviewed",
            "publisher_status": "unverified",
            "auto_review_status": "irrelevant_candidate",
            "auto_review_reason": "non_vocal_role_only",
            "auto_review_checked_at": "2026-11-11T09:00:00+01:00",
        }
        fresh = {"status": "ok", "title": "Updated page"}
        result = grow_sources.carry_review_metadata(fresh, previous)
        self.assertEqual(result["review_status"], "legacy_unreviewed")
        self.assertEqual(result["publisher_status"], "unverified")
        self.assertEqual(result["auto_review_status"], "irrelevant_candidate")
        self.assertEqual(result["auto_review_reason"], "non_vocal_role_only")
        self.assertEqual(result["auto_review_checked_at"], "2026-11-11T09:00:00+01:00")

    def test_evidence_based_audit_survives_refresh_and_is_not_overwritten(self):
        checked_at = "2026-11-12T11:49:52+01:00"
        previous = {
            "review_status": "legacy_unreviewed",
            "publisher_status": "official",
            "auto_review_status": "needs_review",
            "auto_review_reason": "music_project_proposal_not_individual_audition",
            "auto_review_checked_at": checked_at,
            "audit_method": "evidence_based",
            "audit_date": "2026-11-12",
            "relevance_status": "uncertain",
            "confidence": "medium",
            "evidence_urls": ["https://example.org/official-call"],
            "audit_evidence": [{
                "url": "https://example.org/official-call",
                "page_title": "Official call",
                "excerpt": "Music project proposals only.",
                "checked_at": checked_at,
            }],
            "review_notes": "Keep for review; do not activate.",
            "production_activation": False,
        }
        fresh = {
            "status": "ok",
            "title": "Updated page",
            "relevant_lines": ["Audizioni per soprano e tenore"],
        }
        result = grow_sources.carry_review_metadata(fresh, previous)
        grow_sources.apply_legacy_review(result, checked_at="2026-11-13T09:00:00+01:00")
        self.assertEqual(result["auto_review_status"], "needs_review")
        self.assertEqual(result["auto_review_checked_at"], checked_at)
        self.assertEqual(result["audit_method"], "evidence_based")
        self.assertEqual(result["evidence_urls"], previous["evidence_urls"])
        self.assertEqual(result["audit_evidence"], previous["audit_evidence"])
        self.assertFalse(result["production_activation"])

    def test_unaudited_legacy_entries_still_receive_heuristic_screening(self):
        item = {
            "source": "Theatre casting",
            "title": "Audizioni attori",
            "status": "ok",
            "relevant_lines": ["Selezione per attori e attrici"],
        }
        grow_sources.apply_legacy_review(item, checked_at="2026-11-12T11:49:52+01:00")
        self.assertEqual(item["auto_review_status"], "irrelevant_candidate")
        self.assertEqual(item["audit_method"], "heuristic")

    def test_generic_actor_casting_is_rejected(self):
        probe = {
            "status": "ok",
            "source": "Casting",
            "title": "Audizioni attori e attrici",
            "relevant_lines": [
                "Audizioni per attori",
                "Candidature aperte",
                "Selezione per spettacolo teatrale",
            ],
        }
        self.assertEqual(
            grow_sources.candidate_rejection_reason(probe, "https://example.org/casting"),
            "non_vocal_role_only",
        )


if __name__ == "__main__":
    unittest.main()
