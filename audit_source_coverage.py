#!/usr/bin/env python3
"""Incremental weekly coverage audit for registered and pending vocal sources.

This checks source-page reachability and normalized text drift. It does not
approve publishers, extract opportunities, or prove source authenticity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from zoneinfo import ZoneInfo

from scrapling.fetchers import Fetcher

import scrape_sources as core

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
AUDIT = ROOT / ".github" / "audits"
CHECKPOINT = AUDIT / "source-coverage-checkpoint.json"
REPORT = AUDIT / "source-coverage-latest.md"
SOURCE_AUDIT = ROOT / "reports" / "source-audit-baseline-2026-11-10.json"
VOCAL_RE = re.compile(
    r"canto|cantant|soprano|mezzosoprano|contralto|tenore|baritono|basso|"
    r"vocal|voce|young artist|artisti del coro|coro|corale",
    re.IGNORECASE,
)


def now_iso() -> str:
    return datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")


def week_key() -> str:
    now = datetime.now(ZoneInfo("Europe/Rome"))
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, ""))


def source_inventory() -> list[dict]:
    """Use sources.json as the merged registry; join the source audit baseline."""
    inventory: list[dict] = []
    audit_payload = read_json(SOURCE_AUDIT, {})
    audit_by_id = {x.get("source_id"): x for x in audit_payload.get("items", []) if x.get("source_id")}
    audit_by_number = {x.get("legacy_number"): x for x in audit_payload.get("items", []) if x.get("legacy_number") is not None}
    seen_urls: set[str] = set()
    sources = read_json(DATA / "sources.json", [])
    if isinstance(sources, list):
        for item in sources:
            url = item.get("url", "")
            if not url.startswith("http"):
                continue
            canonical = canonical_url(url)
            if canonical in seen_urls:
                continue
            seen_urls.add(canonical)
            number = item.get("number")
            source_id = str(item.get("source_id") or f"source-{number if number is not None else canonical}")
            audit = audit_by_id.get(source_id) or audit_by_number.get(number) or {}
            inventory.append({
                "source_id": source_id,
                "name": item.get("source") or item.get("name") or source_id,
                "url": url,
                "kind": "registered",
                "review_status": audit.get("auto_review_status") or item.get("review_status") or "classification_missing",
                "publisher_status": audit.get("publisher_status") or item.get("publisher_status") or "unverified",
                "relevance_status": audit.get("relevance_status", "unknown"),
                "audit_confidence": audit.get("confidence", "none"),
                "audit_evidence_url": audit.get("evidence_url"),
                "audit_date": audit.get("audit_date"),
            })

    candidates_payload = read_json(DATA / "source_candidates.json", {})
    candidates = candidates_payload.get("items", []) if isinstance(candidates_payload, dict) else []
    for item in candidates:
        url = item.get("url", "")
        if not url.startswith("http"):
            continue
        canonical = canonical_url(url)
        if canonical in seen_urls:
            continue
        seen_urls.add(canonical)
        candidate_id = item.get("candidate_id", canonical)
        source_id = f"candidate-{candidate_id}"
        inventory.append({
            "source_id": source_id,
            "name": item.get("source") or item.get("title") or source_id,
            "url": url,
            "kind": "pending_candidate",
            "review_status": item.get("auto_review_status") or item.get("review_status", "pending_manual_review"),
            "publisher_status": item.get("publisher_status", "unverified"),
            "relevance_status": item.get("relevance_status", "unknown"),
            "audit_confidence": item.get("confidence", "none"),
            "audit_evidence_url": item.get("evidence_url"),
            "audit_date": item.get("audit_date") or item.get("auto_review_checked_at"),
        })
    return sorted(inventory, key=lambda item: (item["kind"], item["source_id"]))


def inventory_hash(inventory: list[dict]) -> str:
    stable = [
        {key: item[key] for key in ("source_id", "url", "kind")}
        for item in inventory
    ]
    payload = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def scan_one(source: dict, previous: dict | None, checked_at: str) -> dict:
    result = {
        "source_id": source["source_id"],
        "name": source["name"],
        "url": source["url"],
        "kind": source["kind"],
        "review_status": source["review_status"],
        "publisher_status": source["publisher_status"],
        "relevance_status": source.get("relevance_status", "unknown"),
        "audit_confidence": source.get("audit_confidence", "none"),
        "audit_evidence_url": source.get("audit_evidence_url"),
        "audit_date": source.get("audit_date"),
        "checked_at": checked_at,
        "status": "error",
        "http_status": None,
        "title": "",
        "normalized_text_sha256": None,
        "text_characters": 0,
        "relevant_line_count": 0,
        "vocal_signal": False,
        "content_changed": False,
        "anomalies": [],
        "error": None,
    }
    try:
        response = Fetcher.get(source["url"], timeout=25, retries=0)
        http_status = getattr(response, "status", None)
        result["http_status"] = http_status
        title = core.clean_line(response.css("title::text").get() or "")
        text = response.get_all_text(separator="\n") or ""
        normalized = "\n".join(core.clean_line(line) for line in text.splitlines() if core.clean_line(line))
        combined = f"{title}\n{normalized}".strip()
        result["title"] = title
        result["text_characters"] = len(normalized)
        result["normalized_text_sha256"] = hashlib.sha256(combined.encode("utf-8")).hexdigest() if combined else None
        result["relevant_line_count"] = len(core.rank_relevant_lines(normalized.splitlines()))
        result["vocal_signal"] = bool(VOCAL_RE.search(combined))
        if http_status in (403, 429):
            result["status"] = "restricted"
        elif http_status is not None and http_status >= 400:
            result["status"] = "http_error"
        elif not combined:
            result["status"] = "extraction_error"
        else:
            result["status"] = "ok"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {str(exc)[:240]}"

    if previous:
        previous_hash = previous.get("normalized_text_sha256")
        current_hash = result.get("normalized_text_sha256")
        result["content_changed"] = bool(previous_hash and current_hash and previous_hash != current_hash)
        if previous.get("status") == "ok" and result["status"] != "ok":
            result["anomalies"].append("previously_accessible_now_failed")
        if previous.get("vocal_signal") and result["status"] == "ok" and not result["vocal_signal"]:
            result["anomalies"].append("vocal_signal_disappeared")
        if result["content_changed"]:
            result["anomalies"].append("normalized_page_text_changed")
        result["last_success_at"] = (
            checked_at if result["status"] == "ok"
            else previous.get("last_success_at") or previous.get("checked_at")
        )
    else:
        result["last_success_at"] = checked_at if result["status"] == "ok" else None
        if result["status"] == "extraction_error":
            result["anomalies"].append("empty_extraction")
    return result


def render_report(state: dict) -> str:
    results = list(state.get("results", {}).values())
    total = state.get("inventory_count", 0)
    checked = len(state.get("completed_source_ids", []))
    remaining = max(total - checked, 0)
    failed = sum(item.get("status") != "ok" for item in results)
    restricted = sum(item.get("status") == "restricted" for item in results)
    changed = sum(bool(item.get("content_changed")) for item in results)
    anomalies = [item for item in results if item.get("anomalies")]
    baseline_available = bool(state.get("previous_cycle_complete"))
    classifications = {}
    for item in results:
        label = item.get("review_status") or "classification_missing"
        classifications[label] = classifications.get(label, 0) + 1
    registered = [item for item in results if item.get("kind") == "registered"]
    candidates = [item for item in results if item.get("kind") == "pending_candidate"]
    lines = [
        "# Weekly source coverage audit",
        "",
        f"- Cycle: {state.get('cycle')}",
        f"- Started: {state.get('started_at')}",
        f"- Last updated: {state.get('updated_at')}",
        f"- Status: **{state.get('scan_status')}**",
        f"- Coverage: **{checked}/{total}** checked; {remaining} remaining",
        f"- Failed/restricted/extraction errors: {failed} (restricted: {restricted})",
        (f"- Changed normalized text hashes: {changed}" if baseline_available else "- Change comparison: first baseline; no previous complete weekly scan exists yet"),
        f"- Sources with anomalies: {len(anomalies)}",
        f"- Registered sources: {len(registered)}; candidate queue entries: {len(candidates)}",
        "- Source review classifications: " + ", ".join(f"{key}={value}" for key, value in sorted(classifications.items())),
        f"- Official + relevant: {sum(item.get('review_status') == 'auto_approved_official' and item.get('relevance_status') == 'relevant' for item in registered)}",
        f"- Third-party + relevant: {sum(item.get('review_status') == 'auto_approved_third_party' and item.get('relevance_status') == 'relevant' for item in registered)}",
        f"- Needs review / irrelevant / unclassified: {sum(item.get('review_status') in ('needs_review', 'irrelevant_candidate', 'classification_missing') for item in registered)}",
        f"- Inventory SHA-256: {state.get('inventory_sha256')} (inventory identity only)",
        "",
        "This scan checks page access and normalized text changes. A successful HTTP response is not proof of official identity, opportunity validity, or complete announcement capture. Text hashes are not publisher signatures.",
        "Keyword/vocal signals are discovery clues only. Source identity and relevance are reported separately from HTTP reachability; source-level approval does not approve every notice on a mixed-purpose page.",
        "",
        "## Exceptions and changes",
        "",
    ]
    notable = [item for item in results if item.get("status") != "ok" or item.get("anomalies") or item.get("content_changed")]
    if not notable:
        if baseline_available:
            lines.append("No failures or content-change anomalies in the sources checked so far.")
        else:
            lines.append("No fetch failures detected. This is the initial baseline; content changes cannot be compared until a later complete weekly scan.")
    else:
        for item in notable:
            lines.append(f"### {item.get('name')} ({item.get('source_id')})")
            lines.append(f"- URL: {item.get('url')}")
            lines.append(f"- Status: {item.get('status')} / HTTP {item.get('http_status')}")
            lines.append(f"- Last success: {item.get('last_success_at') or 'not yet successful'}")
            lines.append(f"- Anomalies: {', '.join(item.get('anomalies') or []) or 'none'}")
            if item.get("error"):
                lines.append(f"- Error: {item['error']}")
            lines.append("")
    lines.extend([
        "## Coverage limitations",
        "",
        "- Pending candidates are monitored separately and are not promoted to approved sources by this scan.",
        "- 403/429, login walls, CAPTCHA and unavailable pages are recorded as monitoring blind spots; no bypass is attempted.",
        "- A page with no vocal keyword signal is an anomaly clue, not proof that the institution has no current opportunity.",
        "- A vocal keyword signal does not establish that a page or individual notice is relevant to classical singers.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=12)
    args = parser.parse_args()
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be positive")

    AUDIT.mkdir(parents=True, exist_ok=True)
    inventory = source_inventory()
    digest = inventory_hash(inventory)
    cycle = week_key()
    state = read_json(CHECKPOINT, {})
    if state.get("cycle") != cycle or state.get("inventory_sha256") != digest:
        prior_complete = state.get("scan_status") == "completed" and state.get("inventory_sha256") == digest
        prior = state.get("results", {}) if prior_complete else {}
        state = {
            "schema_version": 1,
            "cycle": cycle,
            "inventory_sha256": digest,
            "inventory_count": len(inventory),
            "started_at": now_iso(),
            "completed_source_ids": [],
            "results": {},
            "previous_cycle_results": prior,
            "previous_cycle_complete": prior_complete,
            "scan_status": "in_progress",
        }

    state.setdefault("previous_cycle_complete", False)
    inventory_by_id = {item["source_id"]: item for item in inventory}
    for source_id, result in state.get("results", {}).items():
        source = inventory_by_id.get(source_id)
        if source:
            for field in ("review_status", "publisher_status", "relevance_status",
                          "audit_confidence", "audit_evidence_url", "audit_date"):
                result[field] = source.get(field)
    completed = set(state.get("completed_source_ids", []))
    pending = [item for item in inventory if item["source_id"] not in completed]
    batch = pending[:args.batch_size]
    previous_results = state.get("previous_cycle_results", {})
    checked_at = now_iso()
    for index, source in enumerate(batch):
        previous = previous_results.get(source["source_id"])
        state["results"][source["source_id"]] = scan_one(source, previous, checked_at)
        completed.add(source["source_id"])
        state["completed_source_ids"] = sorted(completed)
        state["updated_at"] = now_iso()
        state["scan_status"] = "completed" if len(completed) >= len(inventory) else "in_progress"
        state["inventory_count"] = len(inventory)
        CHECKPOINT.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        if index < len(batch) - 1:
            time.sleep(1.2)

    if len(completed) >= len(inventory):
        state["scan_status"] = "completed"
        state["completed_at"] = now_iso()
    state["updated_at"] = now_iso()
    CHECKPOINT.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render_report(state), encoding="utf-8")
    remaining = max(len(inventory) - len(completed), 0)
    print(json.dumps({
        "cycle": cycle,
        "inventory_count": len(inventory),
        "checked": len(completed),
        "batch_checked": len(batch),
        "remaining": remaining,
        "scan_status": state["scan_status"],
        "checkpoint": str(CHECKPOINT.relative_to(ROOT)),
        "report": str(REPORT.relative_to(ROOT)),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
