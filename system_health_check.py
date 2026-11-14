#!/usr/bin/env python3
"""Read-only health checks for the OperaLab. public site and private operations service."""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BASE_URL = "https://operalirico.github.io/Opera-Lirico"
OPS_URL = "https://opera-lirico-ops.wl19971007.workers.dev"
PUBLIC_BRAND = b"OperaLab."
JSON_FILES = (
    "data/masterclasses.json",
    "data/opportunities.json",
    "data/conservatori.json",
    "data/repertoire.json",
)
PUBLIC_PATHS = (
    "/",
    "/masterclasses.html",
    "/data/masterclasses.json",
    "/data/opportunities.json",
    "/data/conservatori.json",
)

def parse_datetime(value, context):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError(f"{context}: invalid ISO datetime {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{context}: datetime must include a timezone")
    return parsed

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: cannot parse JSON: {exc}") from exc

def check_local_data():
    checked = []
    for relative in JSON_FILES:
        path = ROOT / relative
        if not path.is_file():
            raise ValueError(f"Required public data file is missing: {relative}")
        payload = load_json(path)
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise ValueError(f"{relative}: expected an object with an items array")
        checked.append(relative)

    masterclasses = load_json(ROOT / "data/masterclasses.json")
    schema = load_json(ROOT / "data/masterclass.schema.json")
    required = schema.get("required", [])
    items = masterclasses["items"]
    ids = [item.get("id") for item in items]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("Published masterclasses contain missing or duplicate IDs")

    for index, item in enumerate(items, 1):
        label = f"masterclass #{index} ({item.get('id')})"
        missing = [key for key in required if not item.get(key)]
        if missing:
            raise ValueError(f"{label}: missing required fields: {', '.join(missing)}")
        if item.get("publication_status") != "published" or item.get("review_status") != "verified" or item.get("publisher_status") != "official":
            raise ValueError(f"{label}: public record failed the publication gate")
        if not str(item.get("source_url", "")).startswith("https://"):
            raise ValueError(f"{label}: source_url must use HTTPS")
        evidence = item.get("evidence") or []
        if not evidence:
            raise ValueError(f"{label}: evidence is missing")
        for evidence_index, record in enumerate(evidence, 1):
            evidence_label = f"{label}, evidence #{evidence_index}"
            if not str(record.get("url", "")).startswith("https://") or not str(record.get("excerpt", "")).strip():
                raise ValueError(f"{evidence_label}: evidence URL/excerpt is incomplete")
            parse_datetime(record.get("checked_at"), evidence_label)
        for field in ("checked_at", "last_verified_at", "start_at", "end_at", "application_deadline_at"):
            if item.get(field):
                parse_datetime(item[field], f"{label}.{field}")
        if item.get("start_at") and item.get("end_at") and parse_datetime(item["end_at"], label) < parse_datetime(item["start_at"], label):
            raise ValueError(f"{label}: end_at is earlier than start_at")

    candidates_path = ROOT / "data/masterclass_candidates.json"
    if candidates_path.is_file():
        candidates = load_json(candidates_path)
        candidate_ids = [item.get("candidate_id") for item in candidates.get("items", [])]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("Masterclass candidate queue contains duplicate candidate IDs")
        for item in candidates.get("items", []):
            if item.get("review_status") != "verified" and item.get("publication_status") == "published":
                raise ValueError(f"Unverified candidate {item.get('candidate_id')} is marked published")
    checked.extend(["masterclass publication gate and evidence", "masterclass candidate queue isolation"])
    return checked

def fetch_url(url, attempts=3):
    last_error = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": "OperaLirico-SystemHealth/1.0", "Accept": "*/*"})
            with urlopen(request, timeout=20) as response:
                if response.status != 200:
                    raise RuntimeError(f"{url}: HTTP {response.status}")
                body = response.read()
                if not body:
                    raise RuntimeError(f"{url}: empty response")
                return body
        except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Public endpoint unavailable after {attempts} attempts: {url}: {last_error}")

def check_public_site(base_url):
    checked = []
    for path in PUBLIC_PATHS:
        url = base_url.rstrip("/") + path
        body = fetch_url(url)
        if path.endswith(".json"):
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception as exc:
                raise RuntimeError(f"{url}: response is not valid UTF-8 JSON: {exc}") from exc
            if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
                raise RuntimeError(f"{url}: response JSON has an unexpected structure")
        elif path == "/" and PUBLIC_BRAND not in body:
            raise RuntimeError(f"{url}: homepage response does not contain expected public brand {PUBLIC_BRAND.decode()}")
        elif path == "/masterclasses.html" and PUBLIC_BRAND not in body:
            raise RuntimeError(f"{url}: masterclass page does not contain expected public brand {PUBLIC_BRAND.decode()}")
        checked.append(path)
    return checked

def check_ops_dashboard(base_url):
    root = fetch_url(base_url.rstrip("/") + "/")
    if b"Opera Lirico" not in root or b"\xe8\xbf\x90\xe8\x90\xa5\xe5\x90\x8e\xe5\x8f\xb0" not in root:
        raise RuntimeError("Operations dashboard root is not serving the expected login page")
    health_body = fetch_url(base_url.rstrip("/") + "/api/health")
    try:
        health = json.loads(health_body.decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Operations health endpoint returned invalid JSON: {exc}") from exc
    if health != {"ok": True, "service": "opera-lirico-ops"}:
        raise RuntimeError("Operations health endpoint returned an unexpected response")

    protected_paths = (
        "/api/session",
        "/api/data",
        "/api/content/drafts",
        "/api/masterclasses/candidates",
        "/api/workflows",
        "/api/admin/backup",
    )
    for path in protected_paths:
        request = Request(base_url.rstrip("/") + path, headers={"User-Agent": "OperaLirico-SystemHealth/1.0"})
        try:
            with urlopen(request, timeout=20) as response:
                status = response.status
        except HTTPError as exc:
            status = exc.code
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(f"Operations endpoint {path} could not be reached: {exc}") from exc
        expected = (401, 503) if path == "/api/admin/backup" else (401,)
        if status not in expected:
            raise RuntimeError(f"Protected endpoint {path} returned HTTP {status}; expected one of {expected} without credentials")
    return ["operations dashboard login page", "public runtime health endpoint", *[f"{path} rejects unauthenticated access" for path in protected_paths]]

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    print("OperaLab. read-only health check")
    print(f"Public base URL: {base_url}")
    try:
        local = check_local_data()
        remote = check_public_site(base_url)
        ops = check_ops_dashboard(OPS_URL)
    except Exception as exc:
        print(f"HEALTH CHECK FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: {len(local)} local data and publication checks")
    for item in local:
        print(f"  - {item}")
    print(f"PASS: {len(remote)} deployed public endpoints")
    for item in remote:
        print(f"  - {item}")
    print(f"PASS: {len(ops)} private-dashboard availability and access-control checks")
    for item in ops:
        print(f"  - {item}")
    print("No content was modified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
