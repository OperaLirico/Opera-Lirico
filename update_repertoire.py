#!/usr/bin/env python3
"""Build a local searchable catalogue from the Italian Wikisource song index.

Only a few batched API requests run per daily job. The catalogue cursor is saved
so successive days continue through the source list without repeatedly fetching
the same pages. No score files are downloaded by this script.

Note: Italian Wikisource does not return article text through `prop=extracts`
(the extension only serves intro extracts and returns an empty string for these
source texts), so the page body is read from `prop=revisions` instead.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

API = "https://it.wikisource.org/w/api.php"
USER_AGENT = "VocalItaliaCatalogue/1.0 (https://github.com/wl19971007-lgtm/leo)"
CATALOG = Path(__file__).resolve().parent / "data" / "repertoire.json"
SOURCE_CATEGORY = "Categoria:Canti"
BATCH_SIZE = 12
MAX_NEW_PER_RUN = 8
MAX_TEXT_CHARS = 5000
MIN_TEXT_CHARS = 80
SKIP_TITLE = re.compile(r"^(Indice:|Pagina:|Autore:|Categoria:|Canti\s*\(|Canzoni\s*\(|Raccolta|Opere\s*\()", re.I)
RETRY_STATUS = {429, 500, 502, 503, 504}
INTRO_TEMPLATE = re.compile(r"\{\{\s*Intestazione(.*?)\}\}", re.I | re.S)
FIELD_PAIR = re.compile(r"\|\s*([^=|{}\n]+?)\s*=\s*([^|{}\n]*)")
LETTER = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]")
LANGUAGE_CODES = {
    "italiano": "it", "italiana": "it", "italiano antico": "it", "italiano regionale": "it",
    "latino": "la", "francese": "fr", "tedesco": "de", "inglese": "en", "spagnolo": "es",
    "portoghese": "pt", "russo": "ru", "greco": "el", "napolitano": "it", "siciliano": "it",
    "veneto": "it", "milanese": "it", "romanesco": "it", "piemontese": "it",
}


def api(params: dict) -> dict:
    """Query the MediaWiki API, backing off politely on throttling."""
    query = urlencode({"format": "json", "formatversion": 2, **params})
    url = f"{API}?{query}"
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if "error" in payload:
                raise RuntimeError(json.dumps(payload["error"], ensure_ascii=False))
            return payload
        except HTTPError as exc:
            last_error = exc
            if exc.code not in RETRY_STATUS or attempt == 3:
                raise
            wait = float(exc.headers.get("Retry-After") or 0) or 15 * (attempt + 1)
            print(f"Wikisource returned HTTP {exc.code}; retrying in {min(wait, 90):.0f}s", flush=True)
            time.sleep(min(wait, 90))
        except URLError as exc:
            last_error = exc
            if attempt == 3:
                raise
            time.sleep(10 * (attempt + 1))
    raise last_error  # pragma: no cover - defensive


def category_titles() -> list[str]:
    titles: list[str] = []
    continuation: dict = {}
    while True:
        payload = api({
            "action": "query",
            "list": "categorymembers",
            "cmtitle": SOURCE_CATEGORY,
            "cmtype": "page",
            "cmprop": "title",
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
    """Read page source text for a batch of titles in one request."""
    if not titles:
        return []
    payload = api({
        "action": "query",
        "prop": "revisions|categories",
        "rvprop": "content",
        "rvslots": "main",
        "titles": "|".join(titles),
        "cllimit": "50",
    })
    return payload.get("query", {}).get("pages", [])


def wikitext_of(page: dict) -> str:
    revisions = page.get("revisions") or []
    if not revisions:
        return ""
    return str(revisions[0].get("slots", {}).get("main", {}).get("content", "") or "")


def inline_clean(value: str) -> str:
    value = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", value)
    value = re.sub(r"\[\[([^\]]*)\]\]", r"\1", value)
    value = re.sub(r"'''?", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value.replace("&nbsp;", " ")).strip()


def header_fields(wikitext: str) -> dict[str, str]:
    """Pull author/title/language out of the {{Intestazione}} template."""
    match = INTRO_TEMPLATE.search(wikitext)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for key, value in FIELD_PAIR.findall(match.group(1)):
        lowered = key.casefold()
        cleaned = inline_clean(value)
        if not cleaned:
            continue
        if "musiche" in lowered:
            fields.setdefault("composer", cleaned)
        elif "autore" in lowered:
            fields.setdefault("author", cleaned)
        elif "titolo" in lowered:
            fields.setdefault("title", cleaned)
        elif "lingua" in lowered:
            fields.setdefault("language", cleaned)
    return fields


def language_code(label: str) -> str:
    key = label.strip().casefold()
    if not key:
        return "it"
    if key in LANGUAGE_CODES:
        return LANGUAGE_CODES[key]
    for name, code in LANGUAGE_CODES.items():
        if name in key:
            return code
    return "it"


def plain_text(wikitext: str) -> str:
    """Turn Wikisource source markup into readable lyrics."""
    text = INTRO_TEMPLATE.sub("", wikitext)
    for _ in range(4):
        text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    text = re.sub(r"<poem>|</poem>", "", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[https?://[^\]]*\]", "", text)
    text = re.sub(r"'''?", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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
    known.update(
        normalize(str(alias))
        for item in items
        for alias in (item.get("aliases") or [])
        if alias
    )
    added: list[dict] = []
    checked_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")

    try:
        titles = category_titles()
        candidates = [title for title in titles if not SKIP_TITLE.search(title)]
        print(f"Source category lists {len(candidates)} song pages.", flush=True)
        if not candidates:
            data["scan_cursor"] = 0
        else:
            start = cursor if cursor < len(candidates) else 0
            batch = candidates[start:start + BATCH_SIZE]
            if len(batch) < BATCH_SIZE:
                batch += candidates[:BATCH_SIZE - len(batch)]
            # One request for the whole batch keeps daily traffic small.
            time.sleep(1.5)
            pages = fetch_pages(batch)
            print(f"Fetched source text for {len(pages)} candidate pages in one batch.", flush=True)
            skipped_transclusion = 0
            skipped_short = 0
            for page in pages:
                title = str(page.get("title", "")).strip()
                key = normalize(title)
                wikitext = wikitext_of(page)
                if not title or key in known or not wikitext:
                    continue
                if "<pages" in wikitext:
                    # Proofread-page transclusion: the body lives in the Page:
                    # namespace, so the text here is only a placeholder.
                    skipped_transclusion += 1
                    continue
                text = plain_text(wikitext)
                if not (MIN_TEXT_CHARS <= len(text) <= MAX_TEXT_CHARS) or len(LETTER.findall(text)) < 40:
                    skipped_short += 1
                    continue
                fields = header_fields(wikitext)
                categories = [
                    entry["title"].removeprefix("Categoria:")
                    for entry in (page.get("categories") or [])
                ]
                url = "https://it.wikisource.org/wiki/" + quote(title.replace(" ", "_"), safe="/()'")
                heading = fields.get("title") or ""
                aliases = [heading] if heading and normalize(heading) != key else []
                added.append({
                    "title": title,
                    "aliases": aliases,
                    "composer": fields.get("composer") or fields.get("author") or "作者未标注",
                    "work": "Wikisource · Canti",
                    "voice": "待分类",
                    "kind": "声乐文本",
                    "language": language_code(fields.get("language", "")),
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
            if skipped_transclusion or skipped_short:
                print(
                    f"Skipped {skipped_transclusion} proofread transclusions, "
                    f"{skipped_short} short or oversized pages.",
                    flush=True,
                )
            data["scan_cursor"] = start + len(batch)
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
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Song catalogue: {len(items)} existing + {len(added)} new = {len(data['items'])} items; "
        f"next source cursor {data.get('scan_cursor', 0)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
