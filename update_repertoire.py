#!/usr/bin/env python3
"""Grow the searchable catalogue from the LiederNet Archive.

LiederNet indexes art-song texts (Lieder, mélodies, canzoni, romances, and other
classical vocal works) in more than a hundred languages. Each text page lists
the original poem plus every composer who set it, which is exactly the metadata
the catalogue needs: text, language, poet, composer, and work title.

Ids come from the archive's own sitemap shards (a sequential page walk would
waste almost every request on the gaps between ids). The id list is shuffled
with a fixed seed and consumed with a saved position, so each daily batch spans
the whole archive instead of clustering on one songbook, and the sequence does
not repeat until the list is used up.

Only original-language pages (``id="the-tr"``) are imported; translation pages
(``id="the-text"``) are skipped so the catalogue does not fill up with
translations of texts it already has. Pages whose text has no musical setting
are skipped: a poem nobody has set is not a vocal work. No score or audio files
are downloaded.

Writes ``data/repertoire.json`` only.
"""
from __future__ import annotations

import gzip
import html as htmllib
import json
import random
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

CATALOG = Path(__file__).resolve().parent / "data" / "repertoire.json"
BASE = "https://www.lieder.net/lieder/get_text.html?TextId="
SITEMAP = "https://www.lieder.net/sitemap_{:02d}.xml"
USER_AGENT = "VocalItaliaCatalogue/1.0 (https://github.com/wl19971007-lgtm/leo)"
SHUFFLE_SEED = 20261109
SITEMAP_SHARDS = 20
DAY_SCAN_LIMIT = 48
MAX_NEW_PER_RUN = 12
MIN_TEXT_CHARS = 80
MAX_TEXT_CHARS = 5000
RETRY_STATUS = {429, 500, 502, 503, 504}
TAG = re.compile(r"<[^>]+>")
TITLE_RE = re.compile(r'<div id="tr-title"[^>]*>(.*?)</div>', re.S)
AUTHOR_RE = re.compile(r'<div id="tr-auth"[^>]*>(.*?)</div>', re.S)
LANG_RE = re.compile(r'<div id="tr-lang"[^>]*>.*?<span class="orig">(.*?)</span>', re.S)
LYRICS_RE = re.compile(r'<div id="the-tr"[^>]*>(.*?)</div>', re.S)

LANG_CODES = {
    "english": "en", "italian": "it", "italiano": "it", "french": "fr", "français": "fr",
    "german": "de", "deutsch": "de", "spanish": "es", "español": "es", "russian": "ru",
    "русский": "ru", "swedish": "sv", "svenska": "sv", "norwegian": "no", "norsk": "no",
    "portuguese": "pt", "português": "pt", "dutch": "nl", "nederlands": "nl", "polish": "pl",
    "polski": "pl", "czech": "cs", "čeština": "cs", "hungarian": "hu", "magyar": "hu",
    "finnish": "fi", "suomi": "fi", "greek": "el", "ελληνικά": "el", "latin": "la",
    "latina": "la", "danish": "da", "dansk": "da", "icelandic": "is", "íslenska": "is",
    "welsh": "cy", "cymraeg": "cy", "irish": "ga", "gaeilge": "ga", "hebrew": "he",
    "yiddish": "yi", "japanese": "ja", "korean": "ko", "arabic": "ar", "turkish": "tr",
    "catalan": "ca", "romanian": "ro", "croatian": "hr", "serbian": "sr", "bulgarian": "bg",
    "ukrainian": "uk", "slovenian": "sl", "slovak": "sk", "estonian": "et", "latvian": "lv",
    "lithuanian": "lt", "georgian": "ka", "armenian": "hy", "esperanto": "eo",
    "scottish": "sco", "scots": "sco", "gälisch": "gd", "scottish gaelic": "gd",
    "provençal": "oc", "occitan": "oc", "sardinian": "sc", "sicilian": "scn",
    "neapolitan": "nap", "venetian": "vec", "lombard": "lmo", "romansh": "rm",
    "basque": "eu", "galician": "gl", "asturian": "ast", "afrikaans": "af",
    "sanskrit": "sa", "persian": "fa", "hindi": "hi", "vietnamese": "vi", "thai": "th",
    "chinese": "zh", "mandarin": "zh", "indonesian": "id", "malay": "ms", "tagalog": "tl",
}


def get(url: str) -> str:
    """Fetch a URL, backing off on throttling and then failing soft."""
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=40) as response:
                return response.read().decode("utf-8", "replace")
        except HTTPError as exc:
            if exc.code == 404:
                return ""
            if exc.code not in RETRY_STATUS or attempt == 2:
                raise
            wait = float(exc.headers.get("Retry-After") or 0) or 20 * (attempt + 1)
            print(f"LiederNet returned HTTP {exc.code}; retrying in {min(wait, 60):.0f}s", flush=True)
            time.sleep(min(wait, 60))
        except URLError:
            if attempt == 2:
                raise
            time.sleep(15 * (attempt + 1))
    return ""


def fetch_text(text_id: int) -> str:
    return get(f"{BASE}{text_id}")


def archive_ids() -> list[int]:
    """Collect every text id from the sitemap shards."""
    ids: set[int] = set()
    for shard in range(SITEMAP_SHARDS):
        url = SITEMAP.format(shard)
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=40) as response:
                raw = response.read()
        except HTTPError:
            break
        except URLError as exc:
            print(f"Sitemap shard {shard:02d} unavailable: {exc}", flush=True)
            break
        try:
            xml = gzip.decompress(raw).decode("utf-8", "replace")
        except OSError:
            xml = raw.decode("utf-8", "replace")
        ids.update(int(value) for value in re.findall(r"get_text\.html\?TextId=(\d+)", xml))
        time.sleep(1)
    return sorted(ids)


def clean(markup: str) -> str:
    text = TAG.sub("", markup)
    text = htmllib.unescape(text).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def language_code(label: str) -> str:
    label = clean(label)
    head = label.split("(")[0].strip().casefold()
    if head in LANG_CODES:
        return LANG_CODES[head]
    for name, code in LANG_CODES.items():
        if name and name in label.casefold():
            return code
    return "und"


INSTRUMENT_HINTS = (
    "voice", "orchestra", "piano", "choir", "chorus", "instrument", "strings",
    "organ", "guitar", "ensemble", "continuo", "unaccompanied", "tenor", "soprano",
    "baritone", "mezzo", "bass", "quartet", "duet",
)


def instrumentation_of(item: str) -> str:
    for bracket in re.findall(r"\[(.*?)\]", item, re.S):
        text = clean(bracket)
        low = text.casefold()
        if "verified" in low or "checked" in low:
            continue
        if any(hint in low for hint in INSTRUMENT_HINTS):
            return text
    return ""


def parse_settings(page: str) -> list[dict]:
    """Return the composer settings listed at the top of the page.

    A page with no setting of its own still lists settings of its *translations*
    further down, so the block has to be cut off before those sections, and
    "None yet in the database" has to be treated as no settings at all.
    """
    start = page.find("Musical settings")
    if start < 0:
        return []
    ends = [page.find(marker, start) for marker in ("Available translations", "Settings in other languages")]
    ends = [value for value in ends if value > 0]
    block = page[start:min(ends) if ends else start + 6000]
    if "None yet in the database" in block:
        return []
    out: list[dict] = []
    for item in re.split(r"<li>", block)[1:]:
        anchor = re.search(r"<a[^>]*>(.*?)</a>", item, re.S)
        if not anchor:
            continue
        quoted = re.findall(r'"([^"]*)"', item)
        out.append({
            "composer": clean(anchor.group(1)),
            "title": clean(quoted[0]) if quoted else "",
            "instrumentation": instrumentation_of(item),
        })
    return out


def parse_item(page: str, text_id: int) -> dict | None:
    if 'id="the-tr"' not in page:
        return None
    title_match = TITLE_RE.search(page)
    lyrics_match = LYRICS_RE.search(page)
    if not title_match or not lyrics_match:
        return None
    title = clean(title_match.group(1))
    lyrics = re.sub(r"<pre>|</pre>", "", lyrics_match.group(1), flags=re.I)
    lyrics = TAG.sub("", lyrics)
    lyrics = htmllib.unescape(lyrics).replace("\xa0", " ")
    lyrics = "\n".join(line.rstrip() for line in lyrics.splitlines())
    lyrics = re.sub(r"\n{3,}", "\n\n", lyrics).strip()
    if not title or not (MIN_TEXT_CHARS <= len(lyrics) <= MAX_TEXT_CHARS):
        return None
    lowered = lyrics.casefold()
    if "not currently in the database" in lowered or "as soon as we obtain it" in lowered:
        return None
    cycle = re.match(r"^(.*?)\s*\[[^\]]*(cycle|song cycle|collection)[^\]]*\]\s*$", title, re.I)
    if cycle:
        title = cycle.group(1).strip()
    settings = parse_settings(page)
    if not settings:
        return None
    # Choral and cantata settings are not what this catalogue indexes; it covers
    # solo vocal repertoire (opera excerpts and art songs).
    if any(word in settings[0]["instrumentation"].casefold() for word in ("chorus", "choir")):
        return None
    author = ""
    author_match = AUTHOR_RE.search(page)
    if author_match:
        author = clean(author_match.group(1)).removeprefix("by ").split("(")[0].strip()
    language = "und"
    lang_match = LANG_RE.search(page)
    if lang_match:
        language = language_code(lang_match.group(1))
    primary = settings[0]
    orchestral = "orchestra" in primary["instrumentation"].casefold()
    return {
        "title": title,
        "aliases": [],
        "composer": primary["composer"] or "作者未标注",
        "work": primary["title"] if primary["title"] and primary["title"] != title else "",
        "voice": "待分类",
        "kind": "咏叹调/歌剧选段" if orchestral else "艺术歌曲",
        "language": language,
        "text": lyrics,
        "summary": "LiederNet 收录的声乐文本，中文大意尚未人工翻译。",
        "textSource": f"{BASE}{text_id}",
        "textSourceName": "LiederNet 原文",
        "scoreUrl": None,
        "downloadUrl": None,
        "licenseNote": "原语文本多已进入公版；页面与注释版权归 LiederNet，引用请保留来源链接。",
        "poet": author,
        "settings": settings[:3],
        "autoImported": True,
    }


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9à-ÿ]+", "", value.casefold())


def main() -> None:
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        items = data.get("items", [])
    except Exception:
        data, items = {}, []

    position = int(data.get("lieder_position", 0) or 0)
    known = {normalize(str(item.get("title", ""))) for item in items}
    checked_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")

    scanned = 0
    unreadable = 0
    skipped = 0
    arias: list[dict] = []
    songs: list[dict] = []
    try:
        ids = archive_ids()
        if not ids:
            raise RuntimeError("sitemap returned no text ids")
        order = ids[:]
        random.Random(SHUFFLE_SEED).shuffle(order)
        if position >= len(order):
            position = 0
        batch = order[position:position + DAY_SCAN_LIMIT]
        position += len(batch)
        print(f"Archive lists {len(order)} texts; sampling {len(batch)} ids across the index.", flush=True)
        for text_id in batch:
            scanned += 1
            page = fetch_text(text_id)
            time.sleep(1.0)
            if not page:
                unreadable += 1
                continue
            item = parse_item(page, text_id)
            if not item or normalize(item["title"]) in known:
                skipped += 1
                continue
            known.add(normalize(item["title"]))
            (arias if item["kind"].startswith("咏叹调") else songs).append(item)
    except Exception as exc:
        print(f"LiederNet unavailable: {type(exc).__name__}: {exc}", flush=True)

    added = (arias + songs)[:MAX_NEW_PER_RUN]
    print(
        f"Scanned {scanned} text pages: {unreadable} unreadable, {skipped} skipped, "
        f"{len(arias)} aria/orchestral, {len(songs)} art songs.",
        flush=True,
    )

    data["generated_at"] = checked_at
    data["catalogue_source"] = "LiederNet Archive originals + curated starter works"
    data["lieder_position"] = position
    data["items"] = items + added
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Song catalogue: {len(items)} existing + {len(added)} new = {len(data['items'])} items; "
        f"next position {position}",
        flush=True,
    )


if __name__ == "__main__":
    main()
