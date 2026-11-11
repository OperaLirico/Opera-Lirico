#!/usr/bin/env python3
"""Upload generated social drafts to the authenticated Cloudflare review queue."""
from __future__ import annotations
import base64, json, os, urllib.request, http.cookiejar
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "social-drafts"
BASE = os.environ.get("OPS_DASHBOARD_URL", "https://opera-lirico-ops.wl19971007.workers.dev").rstrip("/")
PASSWORD = os.environ.get("OPS_DASHBOARD_PASSWORD", "")

def request(opener, path, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE + path, data=data, method="GET" if payload is None else "POST",
        headers={"Accept": "application/json", **({"Content-Type": "application/json"} if data else {})},
    )
    with opener.open(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    if not PASSWORD or len(PASSWORD) < 32:
        raise SystemExit("OPS_DASHBOARD_PASSWORD is missing or too short.")
    index_path = OUT / "index.json"
    if not index_path.exists():
        raise SystemExit("Draft index was not generated.")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if not index.get("items"):
        print("No eligible new content. Nothing to upload.")
        return
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    request(opener, "/api/login", {"password": PASSWORD})
    uploaded = 0
    for item in index["items"]:
        image_path = OUT / item["image"]
        text_path = OUT / item["markdown"]
        payload = {
            "id": item["id"],
            "title": item["title"],
            "category": item["category"],
            "source_url": item["source_url"],
            "caption": text_path.read_text(encoding="utf-8"),
            "image_base64": base64.b64encode(image_path.read_bytes()).decode("ascii"),
        }
        req = urllib.request.Request(
            BASE + "/api/content/drafts", data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            method="POST", headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        with opener.open(req, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not result.get("ok"):
            raise RuntimeError(f"Upload failed for {item['id']}")
        uploaded += 1
    print(f"Uploaded {uploaded} draft(s) to the private review queue.")

if __name__ == "__main__":
    main()
