#!/usr/bin/env python3
"""Build a local searchable catalogue from public Italian Wikisource song texts.

The job imports a small number of new pages per daily run, keeps source attribution,
and never fetches sheet-music files. Text links remain attribution links; search
results themselves are rendered from the locally published JSON.
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
    return titles


def fetch_text(title: str) -> tuple[str, list[str]]:
    payload = api({
        "action": "query",
        "prop": "extracts|categories",
        "titles": title,
        "explaintext": "1",
        "exsectionformat": "plain",
        "exchars": str(MAX_TEXT_CHARS),
        "cllimit": "50",
    })
    pages = payload.get("query", {}).get("pages", [])
    if not pages:
        return "", []
    page = pages[0]
    return str(page.get("extract", "")).strip(), [
        item["title"].removeprefix("Categoria:") for item in page.get("categories", [])
    ]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9à-ÿ]+", "", value.casefold())


def main() -> None:
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        items = data.get("items", [])
    except Exception:
        items = []

    known = {normalize(str(item.get("title", ""))) for item in items}
    added: list[dict] = []
    checked_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")

    try:
        candidates = category_titles()
        for title in candidates:
            if len(added) >= MAX_NEW_PER_RUN:
                break
            if normalize(title) in known or SKIP_TITLE.search(title):
                continue
            try:
                text, categories = fetch_text(title)
                if len(text) < 80 or len(text) > MAX_TEXT_CHARS:
                    continue
                # The Wikisource Canti category is a public song-text index.
                # Keep the original source page and its applicable license visible.
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
                known.add(normalize(title))
                time.sleep(0.4)
            except Exception as exc:
                print(f"Skip {title}: {type(exc).__name__}: {exc}", flush=True)
                continue
    except Exception as exc:
        # A source outage must not erase the already-published catalogue.
        print(f"Wikisource catalogue unavailable: {type(exc).__name__}: {exc}", flush=True)

    data = {
        "generated_at": checked_at,
        "catalogue_source": "Wikisource Categoria:Canti + curated starter works",
        "items": items + added,
    }
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Song catalogue: {len(items)} existing + {len(added)} new = {len(data['items'])} items", flush=True)


if __name__ == "__main__":
    main()
