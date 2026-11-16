#!/usr/bin/env python3
"""REA 数据门：解剖事实入库前的强制校验。"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "voice-structures.json"
EVIDENCE = ROOT / "research" / "evidence.json"

GROUPS = {
    "airway", "palate", "tongue", "larynx_cartilage", "larynx_mucosa",
    "intrinsic_muscle", "extrinsic_muscle", "velar_muscle", "tongue_muscle",
    "respiratory",
}
STATUS = {"verified", "pending"}
# layers = 声带分层等子结构细节，允许先于其他字段待核
FIELDS = {"name", "location", "function", "singing_role", "innervation", "evidence", "layers"}

RED_LINES = [
    (r"越紧[^。]*越亮", "混淆闭合与滤波：闭合紧不决定亮度"),
    (r"肌肉[^。]*主动[^。]*振动", "混淆驱动与自激振动"),
    (r"打开喉咙[^。]*压低喉位", "把喉位当唯一变量"),
]


def main():
    errors = 0
    sources = {s["id"] for s in json.loads(EVIDENCE.read_text(encoding="utf-8"))["sources"]}
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    items = doc["structures"]

    ids = [i["id"] for i in items]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        print("FAIL: duplicate ids", dup)
        errors += 1

    idset = set(ids)
    verified = pending = 0

    for item in items:
        sid = item.get("id", "?")
        if item.get("group") not in GROUPS:
            print("FAIL:", sid, "bad group", item.get("group"))
            errors += 1
        if item.get("review_status") not in STATUS:
            print("FAIL:", sid, "bad status")
            errors += 1

        name = item.get("name") or {}
        for k in ("zh", "la", "en"):
            if not name.get(k):
                print("FAIL:", sid, "missing name." + k)
                errors += 1

        if item.get("parent") and item["parent"] not in idset:
            print("FAIL:", sid, "unknown parent", item["parent"])
            errors += 1
        for rel in item.get("related", []):
            if rel not in idset:
                print("FAIL:", sid, "unknown related", rel)
                errors += 1

        for field in item.get("pending_fields", []):
            if field not in FIELDS:
                print("FAIL:", sid, "bad pending field", field)
                errors += 1

        if item["review_status"] == "verified":
            verified += 1
            ev = item.get("evidence") or []
            if not ev:
                print("FAIL:", sid, "verified without evidence")
                errors += 1
            for e in ev:
                if e not in sources:
                    print("FAIL:", sid, "unknown evidence id", e)
                    errors += 1
            for f in ("function", "singing_role"):
                if not item.get(f):
                    print("FAIL:", sid, "verified without", f)
                    errors += 1
        else:
            pending += 1

        text = " ".join(filter(None, [item.get("function"), item.get("singing_role")]))
        for pattern, why in RED_LINES:
            if re.search(pattern, text):
                print("FAIL:", sid, "red line hit:", why)
                errors += 1

    print("entries=%d verified=%d pending=%d evidence=%d errors=%d" % (len(items), verified, pending, len(sources), errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
