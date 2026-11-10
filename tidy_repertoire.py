"""Normalise the aria catalogue before it is published.

The LiederNet scraper reads a setting's work title out of the quoted text of the
list item, but some pages put a catalogue path there by mistake
("/lieder/get_settings.html?ComposerId=..."). Those values are not work titles
and they poison search, so they are dropped here on every run.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DATA = Path("data/repertoire.json")
JUNK = re.compile(r"(?:https?:\/\/)?\S*\/lieder\/\S*|\S*\.html\?\S*", re.I)
NAME_FIELDS = ("title", "work", "composer", "poet")


def clean(value: str) -> str:
    text = JUNK.sub(" ", value)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.strip().strip("·,;:- ")
    if not text:
        return ""
    if "/" in text or "?" in text or text.lower().startswith("http"):
        return ""
    return text


def main() -> int:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    changed = 0
    for item in items:
        for field in NAME_FIELDS:
            value = item.get(field)
            if not isinstance(value, str):
                continue
            cleaned = clean(value)
            if cleaned != value:
                item[field] = cleaned
                changed += 1
    if changed:
        DATA.write_text(
            json.dumps(payload, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
    print(f"tidy_repertoire: cleaned {changed} field(s) across {len(items)} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
