#!/usr/bin/env python3
"""Keep a local copy of the official bando PDFs the site already trusts.

The card used to end at a download button on a third-party site that can move,
expire, or start returning an HTML error page. This step stores the notices the
collector already picked in data/pdfs/ and records the relative path on the item,
so the page can open the file without leaving the site. The original link stays
on the card as the authoritative source.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

DATA = Path("data/conservatori.json")
PDF_DIR = Path("data/pdfs")
TOTAL_LIMIT = 40 * 1024 * 1024
FILE_LIMIT = 12 * 1024 * 1024
COUNT_LIMIT = 30
BANDO_NAME = re.compile(r"bando|ammission|iscrizion", re.I)
NOISE = re.compile(r"graduatoria|esiti|risultat|ammess|inglese|english|elenco", re.I)


def rank(url: str) -> int:
    name = urllib.parse.unquote(url.split("/")[-1]).lower()
    score = 0
    if re.search(r"bando", name):
        score += 4
    if re.search(r"ammission", name):
        score += 3
    if re.search(r"proroga", name):
        score += 2
    if NOISE.search(name):
        score -= 6
    years = [int(y) for y in re.findall(r"20\d{2}", name)]
    if years:
        newest = max(years)
        score += 4 if newest >= 2026 else (0 if newest == 2025 else -4)
    return score


def target_name(url: str, number) -> str:
    raw = urllib.parse.unquote((url.split("/")[-1] or "").split("?")[0])
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-").lower() or "bando"
    if not stem.endswith(".pdf"):
        stem += ".pdf"
    return f"{number}-{stem[:80]}"


def fetch(url: str, path: Path) -> int:
    if path.exists() and path.stat().st_size > 2048:
        return path.stat().st_size
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; leo-site/1.0)"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            blob = response.read(FILE_LIMIT + 1)
    except Exception as error:
        print(f"  skip {url}: {error}")
        return 0
    if len(blob) > FILE_LIMIT or not blob.startswith(b"%PDF"):
        return 0
    path.write_bytes(blob)
    return len(blob)


def main() -> None:
    if not DATA.exists():
        print("no conservatori.json yet")
        return
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    kept = 0
    for item in payload.get("items", []):
        docs = [d for d in (item.get("documents") or []) if BANDO_NAME.search(d)]
        if not docs:
            continue
        academy = (item.get("number") or 0) >= 300
        if not academy and not any(re.search(r"bando", d, re.I) for d in docs):
            continue
        docs = sorted(docs, key=lambda d: (-rank(d), len(d)))
        limit = 2 if academy else 1
        local = []
        for url in docs[:limit]:
            if rank(url) < 0:
                continue
            if kept >= COUNT_LIMIT or total >= TOTAL_LIMIT:
                break
            path = PDF_DIR / target_name(url, item.get("number"))
            size = fetch(url, path)
            if not size:
                continue
            total += size
            kept += 1
            local.append(path.as_posix())
        if local:
            if len(local) == 1:
                item["pdf_local"] = local[0]
            else:
                item.pop("pdf_local", None)
                item["pdf_locals"] = local
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Mirrored {kept} bando PDF(s), {total // 1024} KB")


if __name__ == "__main__":
    main()
