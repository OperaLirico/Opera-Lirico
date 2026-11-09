#!/usr/bin/env python3
"""Drop entries that turned out not to belong to the catalogue.

The early Wikisource pass accepted whatever looked like a sung text, which let
a handful of Italian folk songs and lullabies in with no composer attached.
The site is about opera and art song, so those records are pruned here — after
the workflow has restored the latest published catalogue and before the daily
append, so a removed entry never comes back through the cursor.
"""

from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "repertoire.json"

# composer value used by the Wikisource pass when no author was found
UNATTRIBUTED = "作者未标注"
DROP_KINDS = {"声乐文本"}


def main() -> None:
    if not DATA.exists():
        print("repertoire.json not found; nothing to prune")
        return
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    kept = [
        item
        for item in items
        if not (
            item.get("composer") == UNATTRIBUTED
            and item.get("kind") in DROP_KINDS
            and item.get("autoImported")
        )
    ]
    removed = len(items) - len(kept)
    if not removed:
        print("Nothing to prune")
        return
    payload["items"] = kept
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Pruned {removed} unattributed folk entries; {len(kept)} remain")


if __name__ == "__main__":
    main()
