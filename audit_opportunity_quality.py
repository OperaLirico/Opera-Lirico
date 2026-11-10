#!/usr/bin/env python3
"""Read-only daily quality report for structured opportunities."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "opportunities.json"
OUT = ROOT / ".github" / "audits"
ROME = ZoneInfo("Europe/Rome")
DATE_FIELDS = (
    "application_open_at", "application_deadline_at",
    "audition_start_at", "audition_end_at",
    "performance_start_at", "performance_end_at",
    "checked_at", "last_verified_at",
)


def parse_dt(value):
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def main() -> None:
    now = datetime.now(ROME)
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    published = [item for item in items if item.get("publication_status") == "published"]
    eligible = [
        item for item in published
        if item.get("review_status") == "verified"
        and item.get("publisher_status") == "official"
        and parse_dt(item.get("application_deadline_at"))
        and parse_dt(item.get("application_deadline_at")) > now
    ]
    within_7 = [item for item in eligible if parse_dt(item["application_deadline_at"]) <= now + timedelta(days=7)]
    within_30 = [item for item in eligible if parse_dt(item["application_deadline_at"]) <= now + timedelta(days=30)]
    expired = [
        item for item in published
        if parse_dt(item.get("application_deadline_at"))
        and parse_dt(item["application_deadline_at"]) <= now
    ]
    missing_deadline = [item for item in published if not item.get("application_deadline_at")]
    missing_application = [item for item in published if not item.get("application_url")]
    missing_pdf = [item for item in published if not item.get("official_pdf_url")]
    missing_both = [item for item in published if not item.get("application_url") and not item.get("official_pdf_url")]
    pending = [
        item for item in items
        if item.get("review_status") != "verified" or item.get("publisher_status") != "official"
    ]
    invalid_dates = []
    for item in items:
        for field in DATE_FIELDS:
            value = item.get(field)
            if not value:
                continue
            parsed = parse_dt(value)
            if parsed is None or parsed.astimezone(ROME).utcoffset() != parsed.utcoffset():
                invalid_dates.append({"id": item.get("id"), "field": field, "value": value})
    ids = [item.get("id") for item in items]
    duplicate_ids = sorted({value for value in ids if ids.count(value) > 1})
    stale = []
    for item in published:
        checked = parse_dt(item.get("last_verified_at") or item.get("checked_at"))
        if checked and now - checked > timedelta(days=7):
            stale.append(item)

    def compact(records):
        return [{
            "id": item.get("id"),
            "title": item.get("title"),
            "deadline": item.get("application_deadline_at"),
            "application_url_missing": not bool(item.get("application_url")),
            "official_pdf_missing": not bool(item.get("official_pdf_url")),
            "last_verified_at": item.get("last_verified_at"),
        } for item in records]

    result = {
        "generated_at": now.isoformat(timespec="seconds"),
        "source_file": "data/opportunities.json",
        "total_records": len(items),
        "published_records_in_file": len(published),
        "currently_open_public_records": len(eligible),
        "deadlines_within_7_days": compact(within_7),
        "deadlines_within_30_days": compact(within_30),
        "expired_but_still_published_in_file": compact(expired),
        "published_missing_application_url": compact(missing_application),
        "published_missing_official_pdf_url": compact(missing_pdf),
        "published_missing_both_application_and_pdf": compact(missing_both),
        "published_missing_deadline": compact(missing_deadline),
        "pending_or_non_official_records": compact(pending),
        "stale_verification_over_7_days": compact(stale),
        "invalid_or_non_rome_timezone_dates": invalid_dates,
        "duplicate_ids": duplicate_ids,
        "frontend_publication_gate_violations": compact([
            item for item in published
            if item.get("review_status") != "verified" or item.get("publisher_status") != "official"
        ]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "opportunity-quality-latest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Daily opportunity data quality",
        "",
        f"- Generated: {result['generated_at']} (Europe/Rome)",
        f"- Records in file: {len(items)}",
        f"- Published records in file: {len(published)}",
        f"- Currently open and publication-eligible: {len(eligible)}",
        f"- Deadline within 7 days: {len(within_7)}",
        f"- Deadline within 30 days: {len(within_30)}",
        f"- Expired but still present as published: {len(expired)}",
        f"- Missing application URL: {len(missing_application)}",
        f"- Missing official PDF: {len(missing_pdf)}",
        f"- Missing both application URL and PDF: {len(missing_both)}",
        f"- Missing deadline: {len(missing_deadline)}",
        f"- Pending/non-official: {len(pending)}",
        f"- Verification older than 7 days: {len(stale)}",
        f"- Invalid/non-Europe-Rome offsets: {len(invalid_dates)}",
        f"- Duplicate IDs: {len(duplicate_ids)}",
        "",
        "This is a read-only quality report. It does not change, archive, or publish opportunity records. The website publication gate remains authoritative.",
        "",
    ]
    for title, key in (
        ("Deadlines within 7 days", "deadlines_within_7_days"),
        ("Deadlines within 30 days", "deadlines_within_30_days"),
        ("Expired records still in file", "expired_but_still_published_in_file"),
        ("Records missing both application URL and PDF", "published_missing_both_application_and_pdf"),
        ("Invalid dates", "invalid_or_non_rome_timezone_dates"),
        ("Stale verification", "stale_verification_over_7_days"),
    ):
        lines.extend([f"## {title}", ""])
        rows = result[key]
        if not rows:
            lines.append("No issues.")
        else:
            for row in rows:
                lines.append(f"- {row.get('title') or row.get('id')} — {row.get('deadline') or row.get('value') or 'date unknown'}")
        lines.append("")
    (OUT / "opportunity-quality-latest.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "records": len(items),
        "published": len(published),
        "currently_open": len(eligible),
        "within_7_days": len(within_7),
        "within_30_days": len(within_30),
        "expired_in_file": len(expired),
        "missing_application": len(missing_application),
        "missing_pdf": len(missing_pdf),
        "missing_both": len(missing_both),
        "pending": len(pending),
        "invalid_dates": len(invalid_dates),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
