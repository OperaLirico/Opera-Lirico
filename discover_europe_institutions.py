#!/usr/bin/env python3
"""Discover European higher music education institutions from the AEC directory.

This is an institution-discovery layer, not an admissions scraper. AEC membership
is evidence that an institution belongs to the higher-music-education network;
it is NOT evidence that it offers classical voice or has open admissions.
Official websites are recorded separately and every vocal/admissions field starts
as not_checked until a later, source-specific verification stage.
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

from lxml import html

BASE = "https://aec-music.eu/members/our-members"
OUT = Path(__file__).resolve().parent / "data" / "europe_institutions.json"
USER_AGENT = "OperaLab-Europe-Discovery/1.0 (public institutional research)"
MAX_PAGES = 12
MAX_PROFILE_FETCHES = 50
REQUEST_TIMEOUT = 25
PAUSE_SECONDS = 0.25

# AEC's public member directory includes institutions outside Europe too.
# This allow-list deliberately defines the European pilot boundary.
EUROPEAN_COUNTRIES = {
    "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus",
    "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus",
    "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia",
    "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo",
    "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Moldova, Republic of",
    "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway",
    "Poland", "Portugal", "Romania", "Russian Federation", "San Marino",
    "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland",
    "Turkey", "Ukraine", "United Kingdom", "Vatican City",
}
AEC_DIRECTORY_SOURCE = "https://aec-music.eu/members/our-members"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return response.read()


def text_content(node) -> str:
    return re.sub(r"\s+", " ", " ".join(node.itertext())).strip()


def member_cards(document: bytes, page_url: str) -> list[dict]:
    """Extract member profile links and their nearest country/status context."""
    root = html.fromstring(document)
    records: list[dict] = []
    seen: set[str] = set()
    for anchor in root.xpath("//a[contains(@href, '/member/')]"):
        href = urljoin(page_url, anchor.get("href", ""))
        if not href or href in seen:
            continue
        name = text_content(anchor)
        if not name or name.lower() in {"view member", "member details"}:
            continue
        country_nodes = anchor.xpath("preceding::h2[1]")
        country = text_content(country_nodes[0]) if country_nodes else ""
        if country not in EUROPEAN_COUNTRIES:
            continue

        context = ""
        parent = anchor
        for _ in range(5):
            if parent is None:
                break
            candidate = text_content(parent)
            if "Active members" in candidate or "Associate members" in candidate:
                context = candidate
                break
            parent = parent.getparent()
        status_match = re.search(r"(Active members|Associate members)", context, re.I)
        membership = status_match.group(1).lower().replace(" ", "_") if status_match else "unspecified"
        city = ""
        if context:
            match = re.search(r"([^|,]+),\s*" + re.escape(country), context)
            if match:
                city = match.group(1).strip()
        records.append({
            "id": re.sub(r"[^a-z0-9]+", "-", urlparse(href).path.rstrip("/").split("/")[-1].lower()).strip("-"),
            "institution": name,
            "country": country,
            "city": city or None,
            "aec_membership": membership,
            "aec_profile_url": href,
            "directory_source": AEC_DIRECTORY_SOURCE,
        })
        seen.add(href)
    return records


def official_website(profile_document: bytes, profile_url: str) -> str | None:
    """Prefer the explicitly labelled Website field on the AEC profile."""
    root = html.fromstring(profile_document)
    for node in root.xpath("//li | //tr | //p | //div"):
        label = text_content(node).lower()
        if "website" not in label or len(label) > 700:
            continue
        for href in node.xpath(".//a/@href"):
            absolute = urljoin(profile_url, href)
            host = (urlparse(absolute).hostname or "").lower()
            if absolute.startswith("http") and host and not host.endswith("aec-music.eu"):
                return absolute

    # Fallback: profile text sometimes embeds the institution's domain as a link.
    excluded = ("aec-music.eu", "facebook.com", "instagram.com", "youtube.com",
                "linkedin.com", "x.com", "twitter.com", "mailto:")
    candidates = []
    for anchor in root.xpath("//a[@href]"):
        href = urljoin(profile_url, anchor.get("href", ""))
        host = (urlparse(href).hostname or "").lower()
        if not host or any(term in host for term in excluded):
            continue
        if href.startswith("http"):
            candidates.append(href)
    return candidates[0] if candidates else None


def load_existing() -> dict[str, dict]:
    if not OUT.exists():
        return {}
    try:
        payload = json.loads(OUT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {item["id"]: item for item in payload.get("items", []) if item.get("id")}


def discover() -> dict:
    existing = load_existing()
    discovered: dict[str, dict] = {}
    page_urls = [BASE] + [f"{BASE}/page-{number}" for number in range(2, MAX_PAGES + 1)]
    pages_read = 0
    for page_url in page_urls:
        try:
            document = fetch(page_url)
        except Exception as exc:
            if pages_read == 0:
                raise RuntimeError(f"AEC directory could not be fetched: {exc}") from exc
            print(f"Stopping pagination at {page_url}: {type(exc).__name__}")
            break
        cards = member_cards(document, page_url)
        if not cards:
            break
        pages_read += 1
        for item in cards:
            discovered.setdefault(item["id"], item)

    if not discovered and not existing:
        raise RuntimeError("AEC directory returned no European member records")

    merged = dict(existing)
    new_ids = [key for key in discovered if key not in merged]
    for key, item in discovered.items():
        previous = merged.get(key, {})
        merged[key] = {**item, **previous}
        # Keep directory metadata current while preserving successful profile data.
        merged[key].update({
            "institution": item["institution"],
            "country": item["country"],
            "city": item["city"] or previous.get("city"),
            "aec_membership": item["aec_membership"],
            "aec_profile_url": item["aec_profile_url"],
            "directory_source": AEC_DIRECTORY_SOURCE,
        })

    retryable = [
        key for key, item in merged.items()
        if item.get("country") in EUROPEAN_COUNTRIES
        and item.get("profile_fetch_status") not in {"ok", "no_official_website_listed"}
    ]
    # Process new institutions first, then retry transient profile fetch failures.
    batch = list(dict.fromkeys(new_ids + retryable))[:MAX_PROFILE_FETCHES]
    checked_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    for key in batch:
        item = merged[key]
        try:
            profile = fetch(item["aec_profile_url"])
            website = official_website(profile, item["aec_profile_url"])
            item["official_website"] = website
            item["profile_fetch_status"] = "ok" if website else "no_official_website_listed"
            item["profile_checked_at"] = checked_at
            item["website_host"] = urlparse(website).hostname if website else None
        except Exception as exc:
            item["profile_fetch_status"] = "fetch_error"
            item["profile_error"] = f"{type(exc).__name__}: {exc}"[:240]
            item["profile_last_attempt_at"] = checked_at
        time.sleep(PAUSE_SECONDS)

    for item in merged.values():
        item.setdefault("institution_type", "higher_music_education")
        item.setdefault("vocal_program_status", "not_checked")
        item.setdefault("admissions_status", "not_checked")
        item.setdefault("review_status", "institution_candidate")
        item.setdefault("coverage_layer", "europe")
        item.setdefault("discovery_source", "aec_member_directory")
        if item.get("country") == "Italy":
            item["coverage_note"] = "Italy is monitored by the existing Italian conservatory collector; this record is retained for cross-European indexing."
        else:
            item.setdefault("coverage_note", None)

    items = sorted(merged.values(), key=lambda x: (x.get("country", ""), x.get("city") or "", x.get("institution", "")))
    return {
        "generated_at": checked_at,
        "scope": "Europe",
        "discovery_method": "AEC official member directory; European-country allow-list",
        "source_url": AEC_DIRECTORY_SOURCE,
        "pages_scanned": pages_read,
        "profile_fetches_this_run": len(batch),
        "total_institutions": len(items),
        "countries": sorted({x["country"] for x in items if x.get("country")}),
        "items": items,
    }


def main() -> int:
    payload = discover()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    statuses: dict[str, int] = {}
    for item in payload["items"]:
        status = item.get("profile_fetch_status", "pending")
        statuses[status] = statuses.get(status, 0) + 1
    print(
        f"Europe discovery: {payload['total_institutions']} institutions, "
        f"{len(payload['countries'])} countries, {payload['pages_scanned']} AEC pages; "
        f"profile fetches this run: {payload['profile_fetches_this_run']}; "
        f"profile statuses: {statuses}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
