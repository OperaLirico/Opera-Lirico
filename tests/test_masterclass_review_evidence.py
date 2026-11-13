import unittest
from pathlib import Path


class MasterclassReviewEvidenceContractTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.worker = (root / "ops-dashboard" / "worker.js").read_text(encoding="utf-8")

    def test_verification_requires_official_publisher(self):
        self.assertIn('candidate.publisher_status !== "official"', self.worker)
        self.assertIn('official_source_required', self.worker)

    def test_verification_requires_https_official_evidence_url(self):
        self.assertIn('official_evidence_url_required', self.worker)
        self.assertIn('new URL(officialEvidenceUrl)', self.worker)
        self.assertIn('official_evidence_domain_mismatch', self.worker)

    def test_official_evidence_hostname_normalizes_www_prefix(self):
        self.assertIn(r'replace(/^www\\./, "")', self.worker)

    def test_verification_requires_exact_source_excerpt(self):
        self.assertIn('officialEvidenceExcerpt.length < 40', self.worker)
        self.assertIn('official_evidence_excerpt_required', self.worker)

    def test_dashboard_collects_and_submits_official_evidence(self):
        self.assertIn('官方证据链接', self.worker)
        self.assertIn('官方证据原文摘录', self.worker)
        self.assertIn('official_evidence_url:evidenceUrl', self.worker)
        self.assertIn('official_evidence_excerpt:evidenceExcerpt', self.worker)

    def test_review_record_persists_evidence_without_publishing(self):
        self.assertIn('official_evidence_url: officialEvidenceUrl', self.worker)
        self.assertIn('official_evidence_excerpt: officialEvidenceExcerpt.slice(0, 2000)', self.worker)
        self.assertIn('verified_pending_publication', self.worker)
        self.assertIn('verified_pending_publication', self.worker)


if __name__ == "__main__":
    unittest.main()
