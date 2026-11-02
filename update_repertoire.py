#!/usr/bin/env python3
"""Build a local searchable catalogue from the Italian Wikisource song index.

Only a few batched API requests run per daily job. The catalogue cursor is saved
so successive days continue through the source list without repeatedly fetching
the same pages. No score files are downloaded by this script.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

API = "https://it.wikisource.org/w/api.php"
USER_AGENT = "VocalItaliaCatalogue/1.0 (https://github.com/wl19971007-lgtm/leo)"
CATALOG = Path(__file__).resolve().parent / "data" / "repertoire.json"
BATCH_SIZE = 30
MAX_NEW_PER_RUN = 12
MAX_TEXT_CHARS = 8000
SKIP_TITLE = re.compile(r"^(Indice:|Pagina:|Autore:|Categoria:|Canti\s*\(|Canzoni\s*\(|Raccolta|Opere\s*\()", re.I)


def api(params: dict) -> dict:
    query = urlencode({"format": "json", "formatversion": 2, **params})
    request = Request(f"{API}?{query}", headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def category_titles() -> list[str]:
    titles: list[str] = []
    continuation: dict = {}
    while True:
        payload = api({
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Categoria:Canti",
            "cmtype": "page",
            "cmprop": "title|timestamp",
            "cmsort": "timestamp",
            "cmdir": "desc",
            "cmlimit": "500",
            **continuation,
        })
        titles.extend(
            item["title"] for item in payload.get("query", {}).get("categorymembers", [])
            if item.get("ns") == 0
        )
        continuation = payload.get("continue", {})
        if not continuation:
            break
        time.sleep(1.5)
    return titles


def fetch_pages(titles: list[str]) -> list[dict]:
    if not titles:
        return []
    payload = api({
        "action": "query",
        "prop": "extracts|categories",
        "titles": "|".join(titles),
        "explaintext": "1",
        "exsectionformat": "plain",
        "exchars": str(MAX_TEXT_CHARS),
        "cllimit": "50",
    })
    return payload.get("query", {}).get("pages", [])


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9à-ÿ]+", "", value.casefold())


def main() -> None:
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        items = data.get("items", [])
    except Exception:
        data, items = {}, []

    cursor = int(data.get("scan_cursor", 0) or 0)
    known = {normalize(str(item.get("title", ""))) for item in items}
    added: list[dict] = []
    checked_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")

    try:
        titles = category_titles()
        candidates = [title for title in titles if not SKIP_TITLE.search(title)]
        if not candidates:
            data["scan_cursor"] = 0
        else:
            if cursor >= len(candidates):
                cursor = 0
            batch = candidates[cursor:cursor + BATCH_SIZE]
            if len(batch) < BATCH_SIZE:
                batch += candidates[:BATCH_SIZE - len(batch)]
            # Fetch page text in one batched API request instead of requesting
            # each title separately. This keeps daily traffic small and polite.
            time.sleep(1.5)
            pages = fetch_pages(batch)
            for page in pages:
                title = str(page.get("title", "")).strip()
                text = str(page.get("extract", "")).strip()
                key = normalize(title)
                if not title or key in known or len(text) < 80 or len(text) > MAX_TEXT_CHARS:
                    continue
                categories = [
                    item["title"].removeprefix("Categoria:")
                    for item in page.get("categories", [])
                ]
                url = "https://it.wikisource.org/wiki/" + quote(title.replace(" ", "_"), safe="/()'")
                added.append({
                    "title": title,
                    "aliases": [],
                    "composer": "",
                    "work": "Wikisource · Canti",
                    "voice": "待分类",
                    "kind": "声乐文本",
                    "text": text,
                    "summary": "每日目录自动收录的声乐文本，曲种与声部尚未人工核对。",
                    "textSource": url,
                    "textSourceName": "Wikisource 原文",
                    "scoreUrl": None,
                    "downloadUrl": None,
                    "licenseNote": "请查看来源页的公版或许可标注；转录文本依 Wikisource 适用许可提供出处。",
                    "categories": categories,
                    "autoImported": True,
                })
                known.add(key)
                if len(added) >= MAX_NEW_PER_RUN:
                    break
            data["scan_cursor"] = cursor + len(batch)
            if data["scan_cursor"] >= len(candidates):
                data["scan_cursor"] = 0
    except Exception as exc:
        # Do not retry a throttled/failed batch. Keep the existing catalogue and
        # cursor; the next scheduled run can resume after the rate limit window.
        print(f"Wikisource catalogue unavailable: {type(exc).__name__}: {exc}", flush=True)

    data["generated_at"] = checked_at
    data["catalogue_source"] = "Wikisource Categoria:Canti + curated starter works"
    data["items"] = items + added
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(
        f"Song catalogue: {len(items)} existing + {len(added)} new = {len(data['items'])} items; "
        f"next source cursor {data.get('scan_cursor', 0)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
