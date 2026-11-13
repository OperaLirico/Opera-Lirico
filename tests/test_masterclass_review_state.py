import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MasterclassReviewStateTests(unittest.TestCase):
    def test_worker_uses_file_review_state_and_prioritizes_kv_review(self):
        worker = (ROOT / "ops-dashboard" / "worker.js").read_text(encoding="utf-8")
        start = worker.index("function attachMasterclassReview(item, storedReview) {")
        end = worker.index("\nasync function getDashboardData", start)
        helper = worker[start:end]
        script = helper + """
const rejected = attachMasterclassReview({
  candidate_id: "aaaaaaaaaaaa",
  review_status: "rejected",
  review_notes: "Expired deadline",
  reviewed_at: "2026-11-13T21:40:00+01:00"
}, null);
const pending = attachMasterclassReview({
  candidate_id: "bbbbbbbbbbbb",
  review_status: "pending_manual_review",
  review_notes: "Official source not yet verified"
}, null);
const stored = attachMasterclassReview({
  candidate_id: "cccccccccccc",
  review_status: "rejected",
  review_notes: "Old file review"
}, {
  status: "verified_pending_publication",
  notes: "Newer dashboard review",
  reviewed_at: "2026-11-14T09:00:00+01:00"
});
console.log(JSON.stringify([rejected.review, pending.review, stored.review]));
"""
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            json.loads(result.stdout),
            [
                {
                    "status": "rejected",
                    "notes": "Expired deadline",
                    "official_evidence_url": "",
                    "official_evidence_excerpt": "",
                    "reviewed_at": "2026-11-13T21:40:00+01:00",
                },
                {
                    "status": "pending_manual_review",
                    "notes": "Official source not yet verified",
                    "official_evidence_url": "",
                    "official_evidence_excerpt": "",
                    "reviewed_at": None,
                },
                {
                    "status": "verified_pending_publication",
                    "notes": "Newer dashboard review",
                    "reviewed_at": "2026-11-14T09:00:00+01:00",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
