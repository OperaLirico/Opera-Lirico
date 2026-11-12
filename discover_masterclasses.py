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
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

from scrapling.fetchers import Fetcher

import robots_policy

ROOT = Path(__file__).resolve().parent
SOURCES_PATH = ROOT / "data" / "masterclass_sources.json"
CANDIDATES_PATH = ROOT / "data" / "masterclass_candidates.json"
PUBLISHED_PATH = ROOT / "data" / "masterclasses.json"
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
GENERIC_NAV_RE = re.compile(r"^(?:skip to (?:main )?content|salta al contenuto|vai al contenuto|home|menu|conservatorio|istituzione)$", re.I)
GENERIC_LISTING_RE = re.compile(r"^(?:master.?class(?:es)?(?:\s*[-|–:]\s*.+)?|corsi e master.?class(?:es)?\b.*|courses?\s*[|–-]\s*voice)$", re.I)
NUMERIC_DATE_RE = re.compile(r"\b(\d{1,2})[./-](\d{1,2})[./-](20\d{2})\b")
WORD_DATE_RE = re.compile(r"\b(\d{1,2})\s+([a-zà-ÿ]+)\s+(20\d{2})\b", re.I)
MONTHS = {
    "jan": 1, "january": 1, "gennaio": 1,
    "feb": 2, "february": 2, "febbraio": 2,
    "mar": 3, "march": 3, "marzo": 3,
    "apr": 4, "april": 4, "aprile": 4,
    "may": 5, "maggio": 5,
    "jun": 6, "june": 6, "giugno": 6,
    "jul": 7, "july": 7, "luglio": 7,
    "aug": 8, "august": 8, "agosto": 8,
    "sep": 9, "sept": 9, "september": 9, "settembre": 9,
    "oct": 10, "october": 10, "ottobre": 10,
    "nov": 11, "november": 11, "novembre": 11,
    "dec": 12, "december": 12, "dicembre": 12,
}
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


def has_future_date(value: str) -> bool:
    today = datetime.now(ZoneInfo("Europe/Rome")).date()
    for day, month, year in NUMERIC_DATE_RE.findall(value):
        try:
            if date(int(year), int(month), int(day)) >= today:
                return True
        except ValueError:
            continue
    for day, month_name, year in WORD_DATE_RE.findall(value):
        month = MONTHS.get(month_name.lower().rstrip("."))
        if month:
            try:
                if date(int(year), month, int(day)) >= today:
                    return True
            except ValueError:
                continue
    return False


def canonical_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, ""))


def is_generic_candidate_title(title: str, source_name: str = "") -> bool:
    value = clean(title)
    if not value:
        return True
    if GENERIC_NAV_RE.fullmatch(value) or GENERIC_LISTING_RE.fullmatch(value):
        return True
    source = clean(source_name)
    if source and value.casefold().startswith(source.casefold()):
        suffix = value[len(source):].strip(" -–—|:")
        if not suffix or len(suffix) <= 24:
            return True
    return False


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
        target = canonical_url(urljoin(url, href))
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
    if is_generic_candidate_title(title, source.get("name", "")) and not discovery_label:
        return None
    # Require an event-level title/link label, vocal relevance in the page body,
    # and an explicit date signal. This avoids turning generic navigation pages
    # or evergreen academy descriptions into false opportunity records.
    if not MASTERCLASS_RE.search(" ".join((title, discovery_label))):
        return None
    if not VOICE_RE.search(text):
        return None
    date_signals = DATE_RE.findall(blob)
    if not date_signals or not has_future_date(blob):
        return None
    # Capture a short, human-readable excerpt around the first useful signal.
    match = MASTERCLASS_RE.search(text)
    start = max(0, match.start() - 180) if match else 0
    excerpt = text[start:start + 700].strip()
    label = discovery_label or title or source["name"]
    if is_generic_candidate_title(label, source.get("name", "")):
        label = title or source["name"]
    if is_generic_candidate_title(label, source.get("name", "")):
        return None
    candidate_title = label if len(label) > 8 else title or source["name"]
    normalized_url = canonical_url(url)
    identity = hashlib.sha256((source["id"] + "|" + normalized_url).encode()).hexdigest()[:12]
    return {
        "candidate_id": identity,
        "title_hint": candidate_title[:240],
        "source_name": source["name"],
        "source_type": source.get("source_type", "organizer"),
        "publisher_status": source.get("publisher_status", "unknown"),
        "source_url": normalized_url,
        "discovered_from": source["url"],
        "checked_at": checked_at,
        "discovery_status": "candidate_found",
        "review_status": "pending_manual_review",
        "publication_status": "not_published",
        "date_signals": date_signals[:12],
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


def is_already_published(candidate: dict, published_items: list[dict]) -> bool:
    candidate_url = canonical_url(candidate.get("source_url", ""))
    candidate_title = clean(candidate.get("title_hint", "")).casefold()
    if not candidate_url:
        return False
    for item in published_items:
        if (item.get("publisher_status") != "official"
                or item.get("review_status") != "verified"
                or item.get("publication_status") != "published"):
            continue
        if canonical_url(item.get("source_url", "")) != candidate_url:
            continue
        teacher_names = [clean(part).casefold() for part in (item.get("teacher") or "").split(";")]
        if any(name and name in candidate_title for name in teacher_names):
            return True
        published_title = clean(item.get("title", "")).casefold()
        if published_title and (published_title in candidate_title or candidate_title in published_title):
            return True
    return False


def deduplicate_candidates(items: list[dict]) -> list[dict]:
    """Collapse legacy fragment duplicates while retaining review decisions."""
    merged: dict[tuple[str, str], dict] = {}
    for item in items:
        source = clean(item.get("source_name", "")).casefold()
        url = canonical_url(item.get("source_url", ""))
        key = (source, url)
        previous = merged.get(key)
        if previous is None:
            merged[key] = item
            continue
        # Prefer the freshest record, but never discard a completed human review.
        winner = item if item.get("checked_at", "") >= previous.get("checked_at", "") else previous
        other = previous if winner is item else item
        if other.get("review_status") not in (None, "", "pending_manual_review"):
            winner = {**winner, "review_status": other.get("review_status"),
                      "review_notes": other.get("review_notes", "")}
        elif winner.get("review_notes") in (None, "") and other.get("review_notes"):
            winner = {**winner, "review_notes": other.get("review_notes")}
        winner["source_url"] = url
        aliases = set(previous.get("legacy_candidate_ids", [])) | set(item.get("legacy_candidate_ids", []))
        aliases.update((previous.get("candidate_id"), item.get("candidate_id")))
        aliases.discard(None)
        aliases.discard(winner.get("candidate_id"))
        if aliases:
            winner["legacy_candidate_ids"] = sorted(aliases)
        merged[key] = winner
    return sorted(merged.values(), key=lambda x: (
        x.get("source_name", ""), x.get("title_hint", "")
    ))


def discover() -> dict:
    config = load_json(SOURCES_PATH, {"sources": []})
    old = load_json(CANDIDATES_PATH, {"items": []})
    published = load_json(PUBLISHED_PATH, {"items": []})
    published_items = published.get("items", []) if isinstance(published, dict) else []
    old_by_id = {
        item.get("candidate_id"): item
        for item in old.get("items", [])
        if item.get("candidate_id")
        and "/archivio" not in (item.get("source_url") or "").lower()
        and has_future_date(" ".join(item.get("date_signals", [])))
        and not is_generic_candidate_title(item.get("title_hint", ""), item.get("source_name", ""))
        and not is_already_published(item, published_items)
    }
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
            if candidate and not is_already_published(candidate, published_items):
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
                    if candidate and not is_already_published(candidate, published_items):
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
    deduplicated = deduplicate_candidates(list(merged.values()))
    payload = {
        "updated_at": checked_at,
        "source_count": len(config.get("sources", [])),
        "candidate_count": len(deduplicated),
        "new_or_refreshed_this_run": len(found),
        "fetch_errors": errors,
        "items": deduplicated,
    }
    CANDIDATES_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Found/refreshed {len(found)} masterclass lead(s); {len(merged)} queued. No lead was published.")
    return payload


if __name__ == "__main__":
    discover()
