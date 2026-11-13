#!/usr/bin/env python3
"""Collect Italian opera-libretto excerpts into a private review queue.

This is discovery, not publication: full libretto scenes are not assumed to be
arias. Candidates stay in data/repertoire_candidates.json and are never loaded
by the public frontend. A human must identify the actual aria, voice type,
work/scene metadata, text rights and source evidence before promotion.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from zoneinfo import ZoneInfo

import update_arias as source

ROOT = Path(__file__).resolve().parent
PUBLIC_CATALOG = ROOT / "data" / "repertoire.json"
CANDIDATE_CATALOG = ROOT / "data" / "repertoire_candidates.json"
DAILY_LIMIT = 8
QUEUE_LIMIT = 500


def normalized_title(value: str) -> str:
    value = str(value or "").casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def candidate_id(title: str, page: str) -> str:
    key = f"{normalized_title(title)}|{page}"
    return "wikisource-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"items": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("items", []), list):
        raise ValueError(f"Invalid catalogue structure: {path}")
    return payload


def make_candidate(unit: dict, collected_at: str) -> dict:
    page = str(unit["page"])
    title = str(unit["title"])
    source_url = "https://it.wikisource.org/wiki/" + quote(page.replace(" ", "_"), safe="/()'")
    return {
        "candidate_id": candidate_id(title, page),
        "title": title,
        "aliases": [str(unit.get("work") or "")],
        "composer": str(unit.get("composer") or "作者未标注"),
        "work": str(unit.get("work") or ""),
        "voice": "待核验",
        "kind": "歌剧唱段候选（整场文本）",
        "language": "it",
        "text": str(unit["body"]),
        "summary": "自动收集的歌剧剧本场景文本；并非已确认的独立咏叹调，需人工定位唱段。",
        "textSource": source_url,
        "textSourceName": "意大利 Wikisource · 歌剧剧本",
        "scoreUrl": None,
        "downloadUrl": None,
        "librettist": str(unit.get("librettist") or ""),
        "section": "待审核候选",
        "review_status": "pending",
        "publication_status": "candidate",
        "candidate_reason": "来源按整幕/场景切分，尚未确认其中是否包含独立咏叹调及其边界。",
        "collected_at": collected_at,
        "collection_source": "it.wikisource.org",
    }


def main() -> None:
    public = read_json(PUBLIC_CATALOG)
    queue = read_json(CANDIDATE_CATALOG)
    candidates = queue.get("items", [])
    if len(candidates) >= QUEUE_LIMIT:
        print(f"Candidate queue reached safety limit ({QUEUE_LIMIT}); collection paused.")
        return

    known_titles = {
        normalized_title(item.get("title", ""))
        for item in public.get("items", []) + candidates
        if isinstance(item, dict)
    }
    known_ids = {
        str(item.get("candidate_id", ""))
        for item in candidates
        if isinstance(item, dict)
    }
    opera_index = int(queue.get("aria_opera", 0) or 0)
    scene_index = int(queue.get("aria_scene", 0) or 0)
    collected_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")
    added: list[dict] = []

    operas = source.libretti()
    if not operas:
        raise RuntimeError("Italian Wikisource returned no opera libretti")
    if opera_index >= len(operas):
        opera_index = 0

    opera = operas[opera_index]
    print(f"Scanning libretto {opera_index + 1}/{len(operas)}: {opera}", flush=True)
    units = source.build_units(opera)
    print(f"Found {len(units)} scene-sized text units; resume cursor {scene_index}.", flush=True)

    while scene_index < len(units) and len(added) < DAILY_LIMIT:
        unit = units[scene_index]
        scene_index += 1
        title_key = normalized_title(str(unit.get("title", "")))
        cid = candidate_id(str(unit.get("title", "")), str(unit.get("page", "")))
        if not title_key or title_key in known_titles or cid in known_ids:
            continue
        added.append(make_candidate(unit, collected_at))
        known_titles.add(title_key)
        known_ids.add(cid)

    if scene_index >= len(units):
        opera_index += 1
        scene_index = 0

    queue["generated_at"] = collected_at
    queue["source"] = "Italian Wikisource opera libretti; candidate-only, human review required"
    queue["aria_opera"] = opera_index
    queue["aria_scene"] = scene_index
    queue["items"] = candidates + added
    CANDIDATE_CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATE_CATALOG.write_text(
        json.dumps(queue, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Added {len(added)} review candidates; queue now has {len(queue['items'])}; "
        f"next cursor opera={opera_index}, scene={scene_index}.",
        flush=True,
    )


if __name__ == "__main__":
    main()
