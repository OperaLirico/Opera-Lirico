#!/usr/bin/env python3
"""Build a 30-case human-adjudication benchmark from registered official sources.

This creates an annotation template only. It does not fetch pages, infer labels,
call an AI API, modify production data, or publish opportunities.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
POLICIES = ROOT / "data" / "source_fetch_policies.json"
OUT = ROOT / ".github" / "audits" / "extraction-benchmark-30-template.json"
TARGET_CASES = 30


def main() -> None:
    payload = json.loads(POLICIES.read_text(encoding="utf-8"))
    entries = payload.get("entries", [])
    seen: set[str] = set()
    selected = []
    for entry in entries:
        url = entry.get("url", "").strip()
        source_id = entry.get("source_id", "").strip()
        if not url.startswith(("https://", "http://")) or not source_id or url in seen:
            continue
        seen.add(url)
        selected.append(entry)
        if len(selected) == TARGET_CASES:
            break
    if len(selected) < TARGET_CASES:
        raise SystemExit(f"Need {TARGET_CASES} unique registered sources; found {len(selected)}")

    cases = []
    for index, entry in enumerate(selected, start=1):
        cases.append({
            "case_id": f"official-source-{index:02d}",
            "source_id": entry["source_id"],
            "source_name": entry.get("source_name", entry["source_id"]),
            "source_url": entry["url"],
            "source_strategy_status": entry.get("strategy_status", "unknown"),
            "annotation": {
                "relevance": None,
                "notice_type": None,
                "voice_types": [],
                "application_deadline": None,
                "audition_dates": [],
                "fee_eur": None,
                "eligibility": None,
                "application_url": None,
                "official_document_url": None,
                "evidence_quote": None,
                "evidence_url": None,
                "reviewer": None,
                "reviewed_at": None,
                "notes": ""
            }
        })

    result = {
        "schema_version": 1,
        "generated_at": datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds"),
        "purpose": "Human-adjudicated gold-label template for a 30-source extraction benchmark.",
        "status": "awaiting_manual_annotation",
        "case_count": len(cases),
        "annotation_policy": {
            "relevance_values": ["relevant", "irrelevant", "uncertain"],
            "notice_type_values": ["audition", "choir_recruitment", "vocal_competition", "young_artist", "masterclass", "conservatory_admission", "other", "not_applicable"],
            "rules": [
                "Use the official source page or its linked official notice/document as evidence.",
                "Record exact original wording and the URL supporting each important field.",
                "Use null when a field is absent; do not infer dates, fees, eligibility, or open status.",
                "Mark uncertain when the official evidence conflicts or cannot be read.",
                "Do not promote any benchmark annotation to production data automatically."
            ]
        },
        "cases": cases
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {OUT} with {len(cases)} unlabelled cases.")
    print("No page fetching, AI inference, API calls, or production-data changes were performed.")


if __name__ == "__main__":
    main()
