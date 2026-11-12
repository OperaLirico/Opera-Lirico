#!/usr/bin/env python3
"""Read-only daily quality report for structured opportunities."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
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
DATE_ONLY_FIELDS = ("application_deadline_date",)


def parse_dt(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError):
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def parse_date(value):
    """Parse a true ISO calendar date; never turn it into an invented time."""
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def deadline_is_open(item, now):
    exact = parse_dt(item.get("application_deadline_at"))
    if exact is not None:
        return exact > now
    day = parse_date(item.get("application_deadline_date"))
    return day is not None and day >= now.astimezone(ROME).date()


def deadline_is_expired(item, now):
    exact = parse_dt(item.get("application_deadline_at"))
    if exact is not None:
        return exact <= now
    day = parse_date(item.get("application_deadline_date"))
    return day is not None and day < now.astimezone(ROME).date()


def deadline_within_window(item, now, days):
    exact = parse_dt(item.get("application_deadline_at"))
    if exact is not None:
        return now < exact <= now + timedelta(days=days)
    day = parse_date(item.get("application_deadline_date"))
    if day is None:
        return False
    today = now.astimezone(ROME).date()
    return today <= day <= (today + timedelta(days=days))


def deadline_value(item):
    return item.get("application_deadline_at") or item.get("application_deadline_date")


def deadline_precision(item):
    if item.get("application_deadline_at"):
        return "date_time"
    if item.get("application_deadline_date"):
        return "date_only"
    return "unknown"


def has_application_route(item):
    return bool(item.get("application_url") or item.get("application_email"))


def main() -> None:
    now = datetime.now(ROME)
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    published = [item for item in items if item.get("publication_status") == "published"]
    drafts = [item for item in items if item.get("publication_status") == "draft"]
    eligible = [
        item for item in published
        if item.get("review_status") == "verified"
        and item.get("publisher_status") == "official"
        and deadline_is_open(item, now)
    ]
    within_7 = [item for item in eligible if deadline_within_window(item, now, 7)]
    within_30 = [item for item in eligible if deadline_within_window(item, now, 30)]
    expired = [item for item in published if deadline_is_expired(item, now)]
    missing_deadline = [
        item for item in published
        if not parse_dt(item.get("application_deadline_at"))
        and not parse_date(item.get("application_deadline_date"))
    ]
    missing_application_url = [item for item in published if not item.get("application_url")]
    missing_application_route = [item for item in published if not has_application_route(item)]
    missing_pdf = [item for item in published if not item.get("official_pdf_url")]
    missing_both = [
        item for item in published
        if not has_application_route(item) and not item.get("official_pdf_url")
    ]
    pending = [
        item for item in items
        if item.get("review_status") != "verified"
        or item.get("publisher_status") != "official"
        or item.get("publication_status") != "published"
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
        for field in DATE_ONLY_FIELDS:
            value = item.get(field)
            if value and parse_date(value) is None:
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
            "deadline": deadline_value(item),
            "deadline_precision": deadline_precision(item),
            "application_url_missing": not bool(item.get("application_url")),
            "application_email_missing": not bool(item.get("application_email")),
            "application_route_missing": not has_application_route(item),
            "official_pdf_missing": not bool(item.get("official_pdf_url")),
            "publication_status": item.get("publication_status"),
            "review_status": item.get("review_status"),
            "publisher_status": item.get("publisher_status"),
            "last_verified_at": item.get("last_verified_at"),
        } for item in records]

    gate_violations = [
        item for item in published
        if item.get("review_status") != "verified" or item.get("publisher_status") != "official"
    ]
    result = {
        "generated_at": now.isoformat(timespec="seconds"),
        "source_file": "data/opportunities.json",
        "total_records": len(items),
        "draft_records_in_file": len(drafts),
        "published_records_in_file": len(published),
        "currently_open_public_records": len(eligible),
        "deadlines_within_7_days": compact(within_7),
        "deadlines_within_30_days": compact(within_30),
        "expired_but_still_published_in_file": compact(expired),
        "published_missing_application_url": compact(missing_application_url),
        "published_missing_application_route": compact(missing_application_route),
        "published_missing_official_pdf_url": compact(missing_pdf),
        "published_missing_both_application_and_pdf": compact(missing_both),
        "published_missing_deadline": compact(missing_deadline),
        "pending_or_non_official_records": compact(pending),
        "stale_verification_over_7_days": compact(stale),
        "invalid_or_non_rome_timezone_dates": invalid_dates,
        "duplicate_ids": duplicate_ids,
        "frontend_publication_gate_violations": compact(gate_violations),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "opportunity-quality-latest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# Daily opportunity data quality",
        "",
        f"- Generated: {result['generated_at']} (Europe/Rome)",
        f"- Records in file: {len(items)}",
        f"- Draft candidates in file: {len(drafts)}",
        f"- Published records in file: {len(published)}",
        f"- Currently open and publication-eligible: {len(eligible)}",
        f"- Deadline within 7 days: {len(within_7)}",
        f"- Deadline within 30 days: {len(within_30)}",
        f"- Expired but still present as published: {len(expired)}",
        f"- Missing application URL: {len(missing_application_url)}",
        f"- Missing application route (URL/email): {len(missing_application_route)}",
        f"- Missing official PDF: {len(missing_pdf)}",
        f"- Missing both application route and PDF: {len(missing_both)}",
        f"- Missing deadline: {len(missing_deadline)}",
        f"- Pending/draft/non-official records: {len(pending)}",
        f"- Verification older than 7 days: {len(stale)}",
        f"- Invalid/non-Europe-Rome offsets or date-only values: {len(invalid_dates)}",
        f"- Duplicate IDs: {len(duplicate_ids)}",
        "",
        "This is a read-only quality report. Draft records are not public. The website publication gate remains authoritative.",
        "Date-only deadlines are kept as calendar dates; no cutoff time is inferred. They remain visible through that Europe/Rome date and are labelled as time unspecified.",
        "",
    ]
    for title, key in (
        ("Deadlines within 7 days", "deadlines_within_7_days"),
        ("Deadlines within 30 days", "deadlines_within_30_days"),
        ("Expired records still in file", "expired_but_still_published_in_file"),
        ("Records missing both application route and PDF", "published_missing_both_application_and_pdf"),
        ("Pending/draft/non-official records", "pending_or_non_official_records"),
        ("Invalid dates", "invalid_or_non_rome_timezone_dates"),
        ("Stale verification", "stale_verification_over_7_days"),
    ):
        lines.extend([f"## {title}", ""])
        rows = result[key]
        if not rows:
            lines.append("No issues.")
        else:
            for row in rows:
                deadline = row.get("deadline") or row.get("value") or "date unknown"
                precision = " (date only; time not stated)" if row.get("deadline_precision") == "date_only" else ""
                lines.append(f"- {row.get('title') or row.get('id')} — {deadline}{precision}")
        lines.append("")
    (OUT / "opportunity-quality-latest.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "records": len(items),
        "drafts": len(drafts),
        "published": len(published),
        "currently_open": len(eligible),
        "within_7_days": len(within_7),
        "within_30_days": len(within_30),
        "expired_in_file": len(expired),
        "missing_application_url": len(missing_application_url),
        "missing_application_route": len(missing_application_route),
        "missing_pdf": len(missing_pdf),
        "missing_both": len(missing_both),
        "pending": len(pending),
        "invalid_dates": len(invalid_dates),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
