#!/usr/bin/env python3
"""Discover masterclass leads from a curated source list.

This workflow is deliberately discovery-only: it never publishes a course.
Every lead is queued for human review and must be checked against the original
organizer before it can enter data/masterclasses.json.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

from scrapling.fetchers import Fetcher

import robots_policy

ROOT = Path(__file__).resolve().parent
SOURCES_PATH = ROOT / "data" / "masterclass_sources.json"
CANDIDATES_PATH = ROOT / "data" / "masterclass_candidates.json"
TIMEOUT = 15
DELAY = 1.0
MASTERCLASS_RE = re.compile(
    r"master.?class|masterclass|corso(?:\s+di)?\s+perfezionamento|"
    r"corsi?\s+di\s+canto|vocal\s+(?:course|intensive|coaching)|"
    r"opera\s+(?:academy|studio)|summer\s+(?:program|programme|course)",
    re.I,
)
VOICE_RE = re.compile(
    r"opera\s+singer|opera\s+sing|classical\s+sing|voice|vocal|cantant|"
    r"canto\s+lirico|canto|soprano|mezzosoprano|contralto|tenore|baritono|basso|"
    r"repetiteur|répétiteur|accompanist",
    re.I,
)
NOISE_RE = re.compile(r"privacy|cookie|facebook|instagram|linkedin|youtube|newsletter", re.I)
DATE_RE = re.compile(
    r"\b(?:\d{1,2}[./-]\d{1,2}[./-]20\d{2}|"
    r"\d{1,2}\s+[a-zà-ÿ]+\s+20\d{2}|20(?:26|27|28))\b",
    re.I,
)
MAX_TEXT = 30000
MAX_LINKS = 8


def now_iso() -> str:
    return datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:70] or "masterclass"


def fetch_allowed(url: str):
    """Respect robots.txt and validate every redirect hop before fetching."""
    return robots_policy.fetch_page_with_robots(
        url, Fetcher.get, timeout=TIMEOUT, retries=0, delay=1.2
    )


def extract_page(response, url: str) -> tuple[str, str, list[tuple[str, str]]]:
    title = clean(response.css("title::text").get() or "")
    text = clean(response.get_all_text(separator=" ") or "")[:MAX_TEXT]
    links: list[tuple[str, str]] = []
    seen: set[str] = set()
    for node in response.css("a")[:MAX_LINKS * 4]:
        try:
            label = clean(node.css("::text").get() or "")
            href = (node.css("::attr(href)").get() or "").strip()
        except Exception:
            continue
        target = urljoin(url, href)
        if not target.startswith(("https://", "http://")) or NOISE_RE.search(target):
            continue
        if not (MASTERCLASS_RE.search(label) or MASTERCLASS_RE.search(target)):
            continue
        if target in seen:
            continue
        seen.add(target)
        links.append((label[:180], target))
        if len(links) >= MAX_LINKS:
            break
    return title, text, links


def make_candidate(source: dict, url: str, title: str, text: str, checked_at: str,
                   discovery_label: str = "") -> dict | None:
    blob = " ".join((title, discovery_label, text))
    if not MASTERCLASS_RE.search(blob) or not VOICE_RE.search(blob):
        return None
    # Capture a short, human-readable excerpt around the first useful signal.
    match = MASTERCLASS_RE.search(text)
    start = max(0, match.start() - 180) if match else 0
    excerpt = text[start:start + 700].strip()
    label = discovery_label or title or source["name"]
    candidate_title = label if len(label) > 8 else title or source["name"]
    identity = hashlib.sha256((source["id"] + "|" + url).encode()).hexdigest()[:12]
    return {
        "candidate_id": identity,
        "title_hint": candidate_title[:240],
        "source_name": source["name"],
        "source_type": source.get("source_type", "organizer"),
        "publisher_status": source.get("publisher_status", "unknown"),
        "source_url": url,
        "discovered_from": source["url"],
        "checked_at": checked_at,
        "discovery_status": "candidate_found",
        "review_status": "pending_manual_review",
        "publication_status": "not_published",
        "date_signals": DATE_RE.findall(blob)[:12],
        "evidence_excerpt": excerpt,
        "verification_note": (
            "Discovery signal only. Confirm the organizer, edition, dates, deadline, "
            "eligibility, fees and application link on the original organizer page."
        ),
    }


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def discover() -> dict:
    config = load_json(SOURCES_PATH, {"sources": []})
    old = load_json(CANDIDATES_PATH, {"items": []})
    old_by_id = {x.get("candidate_id"): x for x in old.get("items", [])}
    checked_at = now_iso()
    found: dict[str, dict] = {}
    errors: list[dict] = []

    for source in config.get("sources", []):
        try:
            response, access = fetch_allowed(source["url"])
            status = getattr(response, "status", 0) or 0
            if response is None or not access.get("allowed") or status >= 400:
                errors.append({"source": source["name"], "status": access.get("status"),
                               "http_status": status or access.get("http_status")})
                continue
            page_url = access.get("final_url") or source["url"]
            title, text, links = extract_page(response, page_url)
            candidate = make_candidate(source, source["url"], title, text, checked_at)
            if candidate:
                found[candidate["candidate_id"]] = candidate

            # Follow only clearly labelled masterclass/course links from the
            # source page; never spider arbitrary site navigation.
            for label, target in links:
                try:
                    child, child_access = fetch_allowed(target)
                    child_status = getattr(child, "status", 0) or 0
                    if child is None or not child_access.get("allowed") or child_status >= 400:
                        errors.append({"source": source["name"], "url": target,
                                       "status": child_access.get("status"),
                                       "http_status": child_status or child_access.get("http_status")})
                        continue
                    child_url = child_access.get("final_url") or target
                    child_title, child_text, _ = extract_page(child, child_url)
                    candidate = make_candidate(
                        source, child_url, child_title, child_text, checked_at, label
                    )
                    if candidate:
                        found[candidate["candidate_id"]] = candidate
                except Exception as exc:
                    errors.append({"source": source["name"], "url": target,
                                   "error": type(exc).__name__})
        except Exception as exc:
            errors.append({"source": source.get("name", "unknown"),
                           "error": type(exc).__name__})
        print(f"Checked: {source['name']}", flush=True)
        time.sleep(DELAY)

    # Preserve human decisions and first-seen metadata; discovery never promotes.
    merged = dict(old_by_id)
    for key, fresh in found.items():
        previous = merged.get(key, {})
        merged[key] = {
            **fresh,
            "first_seen_at": previous.get("first_seen_at", checked_at),
            "review_status": previous.get("review_status", "pending_manual_review"),
            "review_notes": previous.get("review_notes", ""),
        }
    payload = {
        "updated_at": checked_at,
        "source_count": len(config.get("sources", [])),
        "candidate_count": len(merged),
        "new_or_refreshed_this_run": len(found),
        "fetch_errors": errors,
        "items": sorted(merged.values(), key=lambda x: (x.get("source_name", ""), x.get("title_hint", ""))),
    }
    CANDIDATES_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Found/refreshed {len(found)} masterclass lead(s); {len(merged)} queued. No lead was published.")
    return payload


if __name__ == "__main__":
    discover()
