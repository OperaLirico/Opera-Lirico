#!/usr/bin/env python3
"""Refresh discovered audition sources daily; discover new ones only weekly.

The daily run refreshes a rotating batch of already-approved sources. The
weekly --discover run additionally harvests outbound links from known official
hubs, verifies candidates, and appends qualifying sources. This avoids
repeating candidate searches every day.

All known sources are merged into data/sources.json for the site."""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

import scrape_sources as core

DATA = Path(__file__).resolve().parent / "data"
REGISTRY = DATA / "sources_extra.json"
PAGE = DATA / "sources.json"

BATCH = 12           # discovered pages refreshed per run
MAX_NEW = 8          # new sources accepted per run
MAX_CANDIDATES = 18  # outbound links inspected per run
TIMEOUT = 30

# A link worth following: it names an audition/competition, or lives on such a page.
LINK_TEXT_RE = re.compile(r"audizion|audition|concors|concor|bando|candidat|casting|selezion", re.IGNORECASE)
LINK_PATH_RE = re.compile(r"audizion|concors|bando|casting|selezion|lavora-con-noi|bandi", re.IGNORECASE)
SKIP_HOST_RE = re.compile(
    r"facebook|instagram|twitter|x\.com|youtube|linkedin|whatsapp|tiktok|google|apple|spotify"
    r"|wa\.me|wa\.link|t\.me|m\.me|bit\.ly|tinyurl|goo\.gl", re.IGNORECASE,
)
# Aggregators put share buttons next to every notice; they are not sources.
SHARE_LABEL_RE = re.compile(r"share|condividi|whatsapp|telegram|invia|copia link|stampa", re.IGNORECASE)
SKIP_EXT_RE = re.compile(r"\.(pdf|jpg|jpeg|png|gif|zip|doc|docx|xls|xlsx|mp3|mp4)($|\?)", re.IGNORECASE)
GENERIC_LABEL = re.compile(r"(?i)(apri( il bando)?|leggi|scopri|qui|dettagli|vai|apri il bando→|→|&rarr;)")
# Page chrome and civic portals are reachable and keyword-rich, yet they are not
# audition pages; keep them out of the source list.
CHROME_RE = re.compile(r"sito istituzionale|clicca qui|compila|modulo di domanda|invia la domanda", re.IGNORECASE)
# A theatre also advertises ushering, box office and back-office jobs. Those pages
# are full of call-for-application wording but have nothing to do with singing.
STAFF_RE = re.compile(
    r"maschere|accoglienza|amministra|personale|biglietteria|tirocin|segreteria|addett|"
    r"operatore|magazzino|cassier|autista|guardaroba|organico",
    re.IGNORECASE,
)
PORTAL_RE = re.compile(r"trasparenza|amm\.trasp|archivio/archiviobandi", re.IGNORECASE)
OFFTOPIC_RE = re.compile(
    r"coreograf|danza|danzator|balletto|concorso di scrittura|racconto breve|concorso letterario",
    re.IGNORECASE,
)
AUDITIONISH_RE = re.compile(
    r"audizion|audition|concors|concor|casting|bando|selezion|open ?call|premio|provino|cantanti|orchestra|coro",
    re.IGNORECASE,
)
MIN_LINES = 3


def now_iso() -> str:
    return datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")


def load(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def fetch(url: str):
    response = core.Fetcher.get(url, timeout=TIMEOUT, retries=0)
    status = getattr(response, "status", None) or 0
    title = core.clean_line(response.css("title::text").get() or "")
    text = response.get_all_text(separator="\n") or ""
    lines = [core.clean_line(x) for x in text.splitlines()]
    lines = [x for x in lines if x]
    return {
        "status": "ok" if status < 400 else "http_error",
        "http_status": status,
        "title": title,
        "relevant_lines": core.rank_relevant_lines(lines),
        "response": response,
    }


def scrape_entry(url: str, name: str, number: int, discovered_from: str = "") -> dict:
    item = {
        "number": number,
        "source": name,
        "url": url,
        "checked_at": now_iso(),
        "status": "error",
        "http_status": None,
        "title": "",
        "relevant_lines": [],
        "error": None,
    }
    if discovered_from:
        item["discovered_from"] = discovered_from
    try:
        page = fetch(url)
        item["http_status"] = page["http_status"]
        item["status"] = page["status"]
        item["title"] = page["title"]
        item["relevant_lines"] = page["relevant_lines"]
        item["_response"] = page["response"]
    except Exception as exc:
        item["error"] = f"{type(exc).__name__}: {exc}"
    return item


def harvest_links(response, base_url: str) -> list[tuple[str, str]]:
    try:
        nodes = response.css("a")
    except Exception:
        return []
    out: list[tuple[str, str]] = []
    for node in nodes:
        try:
            label = node.css("::text").get() or ""
            href = node.css("::attr(href)").get() or ""
        except Exception:
            continue
        if not href:
            continue
        target = urljoin(base_url, href.strip())
        if not target.startswith("http") or SKIP_HOST_RE.search(target) or SKIP_EXT_RE.search(target):
            continue
        if SHARE_LABEL_RE.search(label) or SHARE_LABEL_RE.search(target):
            continue
        if not (LINK_TEXT_RE.search(label) or LINK_PATH_RE.search(target)):
            continue
        out.append((core.clean_line(label)[:90], target.split("#")[0]))
    return out


def known_hosts(known: list[dict]) -> set[str]:
    hosts = set()
    for item in known:
        host = urlparse(item.get("url", "")).netloc.lower()
        if host:
            hosts.add(host.removeprefix("www."))
    return hosts


def hub_rank(candidate: tuple[str, str, str]) -> tuple[int, int]:
    """Listing pages age well; single-notice permalinks expire. Prefer hubs."""
    url = candidate[1]
    last = url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
    return (1 if re.search(r"\d{4,}", last) else 0, url.count("/"))


def main(discover: bool = False) -> None:
    payload = load(REGISTRY, {})
    registry: list[dict] = payload.get("items", [])
    cursor: int = int(payload.get("cursor", 0))
    # Candidate discovery is anchored to the curated core list, not every extra URL.
    core_numbers = {source[0] for source in core.SOURCES}
    core_items: list[dict] = [
        item for item in load(PAGE, [])
        if item.get("number") in core_numbers
    ]

    # Drop anything that slipped through earlier rules (share links, files,
    # jobs for ushers and box office, transparency portals, dance and writing
    # competitions).
    cleaned = [
        item for item in registry
        if not SKIP_HOST_RE.search(item.get("url", ""))
        and not SKIP_EXT_RE.search(item.get("url", ""))
        and not CHROME_RE.search(" ".join([item.get("source", ""), item.get("title", "")]))
        and not STAFF_RE.search(" ".join([item.get("source", ""), item.get("title", ""), item.get("url", "")]))
        and not PORTAL_RE.search(item.get("url", ""))
        and not OFFTOPIC_RE.search(" ".join([item.get("source", ""), item.get("title", "")]))
    ]
    if len(cleaned) != len(registry):
        print(f"[extra] removed {len(registry) - len(cleaned)} non-source link(s)", flush=True)
    registry = cleaned
    for item in registry:
        item.pop("_response", None)

    # 1. Refresh a rotating slice of the discovered list.
    batch: list[dict] = []
    if registry:
        start = cursor % len(registry)
        batch = [registry[(start + i) % len(registry)] for i in range(min(BATCH, len(registry)))]
    refreshed: list[dict] = []
    for item in batch:
        fresh = scrape_entry(item["url"], item["source"], item["number"], item.get("discovered_from", ""))
        fresh.pop("_response", None)
        if fresh["status"] == "ok":
            fresh["discovered_at"] = item.get("discovered_at", fresh["checked_at"])
            refreshed.append(fresh)
            print(f"[extra] ok {fresh['http_status']} {fresh['source'][:40]}", flush=True)
        else:
            # Keep the last good extract rather than blanking a working source.
            item["checked_at"] = fresh["checked_at"]
            item["http_status"] = fresh["http_status"]
            item["error"] = fresh["error"]
            item["misses"] = int(item.get("misses", 0)) + 1
            refreshed.append(item)
            print(f"[extra] fail {fresh['http_status']} {item['source'][:40]}", flush=True)
        time.sleep(1.2)
    cursor = (cursor + len(batch)) % max(len(registry), 1)

    # Preserve the full registry; only replace entries in the batch checked today.
    by_number: dict[int, dict] = {item["number"]: item for item in registry}
    by_number.update({item["number"]: item for item in refreshed})
    added = 0

    if discover:
        # 2. Harvest new candidates from known official hubs (weekly only).
        seen = known_hosts(core_items + registry)
        candidates: list[tuple[str, str, str]] = []
        for item in core_items:
            if len(candidates) >= MAX_CANDIDATES:
                break
            if item.get("status") != "ok":
                continue
            if not re.search(r"audizion|concor|bando|casting|bandi|selezion|lavora", item["url"], re.IGNORECASE):
                continue
            try:
                page = fetch(item["url"])
            except Exception:
                continue
            hosts = {urlparse(c[1]).netloc.lower().removeprefix("www.") for c in candidates}
            for label, target in harvest_links(page["response"], item["url"]):
                host = urlparse(target).netloc.lower().removeprefix("www.")
                if host in seen or host in hosts:
                    continue
                hosts.add(host)
                candidates.append((label, target, item["url"]))
                if len(candidates) >= MAX_CANDIDATES:
                    break
            time.sleep(1.2)

        candidates.sort(key=hub_rank)
        next_number = max([item["number"] for item in registry + core_items] + [28]) + 1
        for label, target, origin in candidates:
            if added >= MAX_NEW:
                break
            probe = scrape_entry(target, label or target, next_number, origin)
            probe.pop("_response", None)
            blob = " ".join([probe.get("source", ""), probe.get("title", "")] + probe["relevant_lines"])
            if (
                probe["status"] != "ok"
                or len(probe["relevant_lines"]) < MIN_LINES
                or not AUDITIONISH_RE.search(blob)
                or CHROME_RE.search(probe.get("title", ""))
                or STAFF_RE.search(blob)
                or PORTAL_RE.search(target)
                or OFFTOPIC_RE.search(blob)
            ):
                print(f"[extra] skip {probe['status']} {target[:70]}", flush=True)
                continue
            if len(label) < 12 or GENERIC_LABEL.fullmatch(label.strip() or "x"):
                host = urlparse(target).netloc.removeprefix("www.")
                probe["source"] = (probe["title"] or host)[:70]
            probe["discovered_at"] = probe["checked_at"]
            by_number[next_number] = probe
            next_number += 1
            added += 1
            print(f"[extra] new {probe['http_status']} {probe['source'][:50]} — {target[:60]}", flush=True)
            time.sleep(1.2)
    else:
        print("Discovery skipped; refreshing the existing registry only.", flush=True)

    # A discovered notice page eventually expires; stop carrying dead links.
    keep = [
        item for item in by_number.values()
        if item.get("status") == "ok" or int(item.get("misses", 0)) < 4
    ]
    dropped = len(by_number) - len(keep)
    if dropped:
        print(f"[extra] dropped {dropped} expired source(s)", flush=True)
    registry_out = sorted(keep, key=lambda item: item["number"])

    REGISTRY.write_text(
        json.dumps({"updated_at": now_iso(), "cursor": cursor, "items": registry_out},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 4. Publish the merged list the site renders.
    merged = list(core_items) + registry_out
    PAGE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"registry={len(registry_out)} new={added} merged={len(merged)} next_cursor={cursor}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh known sources; optionally discover new ones.")
    parser.add_argument("--discover", action="store_true", help="harvest and verify new candidates (weekly workflow)")
    args = parser.parse_args()
    main(discover=args.discover)
