#!/usr/bin/env python3
"""Add opera excerpts from the Italian Wikisource libretto collection.

LiederNet is an art-song archive: opera arias are only a small slice of it. The
canonical Italian opera texts live on Italian Wikisource as full libretti
(``Categoria:Libretti d'opera``), where each act is either a subpage or a set of
proofread pages.

A libretto is a whole evening's text, not a single number, and the source does
not mark aria boundaries reliably. So one catalogue entry is one *scene*: act,
scene, composer, librettist and the complete verse of that scene. The aria itself
is inside that text, which means searching its first line ("Sempre libera",
"Libiamo ne' lieti calici") still finds it.

One opera is processed per run, a few scenes at a time, with a saved cursor, so
the collection keeps growing day after day without hammering the source.
"""
from __future__ import annotations

import html as htmllib
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
CATEGORY = "Categoria:Libretti d'opera"
# Canonical Italian repertoire first; the rest of the collection follows
# alphabetically. Operas missing from the source are simply skipped.
PRIORITY = [
    "La traviata", "La bohème", "Le nozze di Figaro", "Don Giovanni", "Pagliacci",
    "Le Villi", "Gianni di Parigi", "Saffo in Leucade", "Tebaldo e Isolina",
    "Didone abbandonata", "Catone in Utica", "Artaserse", "Il sogno di Scipione",
]
ARIA_PER_RUN = 8
MAX_TEXT_CHARS = 5000
MIN_TEXT_CHARS = 120
RETRY_STATUS = {429, 500, 502, 503, 504}
INSTRUMENT = re.compile(r"^(PERSONAGGI|Personaggi|ATTO|Atto)\b")
SCENE_MARK = re.compile(r"^(?:SCENA|Scena)\s+([IVXLCDM]+|[A-Za-zÀ-ÿ]+)\.?\s*$")
NOISE = re.compile(
    r"^(\[p\.\s*\d+.*\]|Informazioni sulla fonte del testo|◄|►|Questo testo è riletto"
    r"|<\w+.*>|//it\.wikisource\.org.*|\d{10,}|.*\.djvu.*)$"
)
ORDINALS = {
    "primo": "I", "secondo": "II", "terzo": "III", "quarto": "IV", "quinto": "V",
    "sesto": "VI", "settimo": "VII", "ottavo": "VIII", "nono": "IX", "decimo": "X",
    "prima": "I", "seconda": "II", "terza": "III", "quarta": "IV", "quinta": "V",
    "sesta": "VI", "settima": "VII", "ottava": "VIII", "nona": "IX", "decima": "X",
    "undicesima": "XI", "dodicesima": "XII", "tredicesima": "XIII", "quattordicesima": "XIV",
    "quindicesima": "XV", "sedicesima": "XVI", "diciassettesima": "XVII",
}


def api(params: dict) -> dict:
    query = urlencode({"format": "json", "formatversion": 2, **params})
    url = f"{API}?{query}"
    for attempt in range(4):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if "error" in payload:
                raise RuntimeError(json.dumps(payload["error"], ensure_ascii=False))
            return payload
        except HTTPError as exc:
            if exc.code not in RETRY_STATUS or attempt == 3:
                raise
            wait = float(exc.headers.get("Retry-After") or 0) or 20 * (attempt + 1)
            print(f"Wikisource returned HTTP {exc.code}; retrying in {min(wait, 60):.0f}s", flush=True)
            time.sleep(min(wait, 60))
        except URLError:
            if attempt == 3:
                raise
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("unreachable")


def libretti() -> list[str]:
    payload = api({"action": "query", "list": "categorymembers", "cmtitle": CATEGORY,
                   "cmtype": "page", "cmlimit": "100"})
    titles = [item["title"] for item in payload.get("query", {}).get("categorymembers", [])
              if item.get("ns") == 0]

    def rank(title: str) -> tuple[int, str]:
        if title in PRIORITY:
            return (0, f"{PRIORITY.index(title):03d}")
        return (1, title.casefold())

    return sorted(titles, key=rank)


def subpages(title: str) -> list[str]:
    payload = api({"action": "query", "list": "allpages", "apprefix": f"{title}/", "aplimit": "40"})
    return [item["title"] for item in payload.get("query", {}).get("allpages", [])]


def wikitext(title: str) -> str:
    payload = api({"action": "query", "prop": "revisions", "rvprop": "content",
                   "rvslots": "main", "titles": title})
    page = payload.get("query", {}).get("pages", [{}])[0]
    revisions = page.get("revisions") or [{}]
    return str(revisions[0].get("slots", {}).get("main", {}).get("content", "") or "")


def rendered_lines(title: str) -> list[str]:
    payload = api({"action": "parse", "page": title, "prop": "text",
                   "disablelimitreport": "1", "disableeditsection": "1"})
    markup = payload.get("parse", {}).get("text", "")
    markup = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", markup, flags=re.S | re.I)
    markup = re.sub(r"</(p|div|li|h\d|tr|dd|dt)>", "\n", markup, flags=re.I)
    markup = re.sub(r"<br\s*/?>", "\n", markup, flags=re.I)
    text = htmllib.unescape(re.sub(r"<[^>]+>", "", markup))
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return [line for line in lines if line and not NOISE.match(line)]


def metadata(wikitext_text: str) -> dict:
    found: dict[str, str] = {}
    for key, value in re.findall(r"\|\s*([^=|{}\n]+?)\s*=\s*([^|{}\n]*)", wikitext_text):
        label = key.casefold()
        clean_value = re.sub(r"\[\[|\]\]|<[^>]+>|'''?", "", value).strip()
        if not clean_value:
            continue
        if "autore delle musiche" in label:
            found.setdefault("composer", clean_value)
        elif "autore" in label:
            found.setdefault("librettist", clean_value)
        elif "titolo" in label:
            found.setdefault("title", clean_value)
    return found


def scenes(lines: list[str]) -> list[tuple[str, str]]:
    """Split rendered act text into (scene label, scene body) pairs."""
    out: list[list[str]] = []
    labels: list[str] = []
    current: list[str] | None = None
    label = "整幕"
    for line in lines:
        match = SCENE_MARK.match(line)
        if match:
            if current:
                out.append(current)
                labels.append(label)
            marker = match.group(1).lower()
            label = ORDINALS.get(marker, marker.upper() if match.group(1).isalpha() else match.group(1))
            label = f"Scena {label}"
            current = []
            continue
        if current is not None:
            current.append(line)
    if current:
        out.append(current)
        labels.append(label)
    if not out:
        body = [line for line in lines if not INSTRUMENT.match(line)]
        return [("整幕", "\n".join(body))]
    return [(label, "\n".join(body)) for label, body in zip(labels, out)]


def act_label(page_title: str, opera: str) -> str:
    tail = page_title[len(opera):].strip("/ ").strip()
    if not tail:
        return ""
    tail = re.sub(r"^(Atto|ATTO)\s+", "", tail, flags=re.I).strip()
    mapped = ORDINALS.get(tail.casefold())
    if mapped:
        return f"Atto {mapped}"
    return tail.capitalize() if tail.isalpha() else tail


def build_units(opera: str) -> list[dict]:
    """Every scene of one opera, in reading order."""
    units: list[dict] = []
    parts = subpages(opera)
    parts = [part for part in parts
             if not re.search(r"(Personaggi|Interlocutori|Argomento|Orchestra|Indice|Note|Frontespizio)", part, re.I)]
    if not parts:
        parts = [opera]
    meta = metadata(wikitext(opera))
    opera_title = meta.get("title") or opera
    for part in parts:
        try:
            lines = rendered_lines(part)
        except Exception as exc:
            print(f"  {part}: {type(exc).__name__}: {exc}", flush=True)
            continue
        time.sleep(1.5)
        act = act_label(part, opera)
        for scene_label, body in scenes(lines):
            if not (MIN_TEXT_CHARS <= len(body) <= MAX_TEXT_CHARS):
                continue
            units.append({
                "title": " · ".join(x for x in (opera_title, act, scene_label) if x),
                "body": body,
                "act": act,
                "scene": scene_label,
                "composer": meta.get("composer") or "作者未标注",
                "librettist": meta.get("librettist", ""),
                "work": opera_title,
                "page": part,
            })
    return units


def main() -> None:
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        items = data.get("items", [])
    except Exception:
        data, items = {}, []

    opera_index = int(data.get("aria_opera", 0) or 0)
    scene_index = int(data.get("aria_scene", 0) or 0)
    known = {str(item.get("title", "")) for item in items}
    added: list[dict] = []
    checked_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")

    try:
        operas = libretti()
        if not operas:
            raise RuntimeError("libretto category returned no pages")
        if opera_index >= len(operas):
            opera_index = 0
        opera = operas[opera_index]
        print(f"Opera {opera_index + 1}/{len(operas)}: {opera}", flush=True)
        units = build_units(opera)
        print(f"  {len(units)} scenes available; resuming at {scene_index}.", flush=True)
        while scene_index < len(units) and len(added) < ARIA_PER_RUN:
            unit = units[scene_index]
            scene_index += 1
            if unit["title"] in known:
                continue
            known.add(unit["title"])
            added.append({
                "title": unit["title"],
                "aliases": [unit["work"]],
                "composer": unit["composer"],
                "work": unit["work"],
                "voice": "待分类",
                "kind": "歌剧选段",
                "language": "it",
                "text": unit["body"],
                "summary": "歌剧剧本选段，含本场全部唱词；搜索唱段首句即可定位。",
                "textSource": "https://it.wikisource.org/wiki/" + quote(unit["page"].replace(" ", "_"), safe="/()'"),
                "textSourceName": "Wikisource 剧本",
                "scoreUrl": None,
                "downloadUrl": None,
                "licenseNote": "剧本原文为公版；Wikisource 转录依 CC BY-SA 提供，引用请保留来源链接。",
                "poet": unit["librettist"],
                "autoImported": True,
            })
        if scene_index >= len(units):
            opera_index += 1
            scene_index = 0
    except Exception as exc:
        print(f"Libretto source unavailable: {type(exc).__name__}: {exc}", flush=True)

    data["generated_at"] = checked_at
    data["aria_opera"] = opera_index
    data["aria_scene"] = scene_index
    data["items"] = items + added
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {len(added)} opera scenes; catalogue now {len(data['items'])} items; "
          f"next opera {opera_index}, scene {scene_index}", flush=True)


if __name__ == "__main__":
    main()
