#!/usr/bin/env python3
"""Create a local PDF byte-integrity manifest; never claim publisher signature verification."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PDF_DIR = DATA / "pdfs"
OUT = ROOT / ".github" / "audits" / "pdf-integrity-manifest.json"


def inspect_pdf(path: Path) -> dict:
    if not path.exists():
        return {"integrity_status": "missing", "size_bytes": 0, "sha256": None}
    digest = hashlib.sha256()
    size = 0
    prefix = b""
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            if len(prefix) < 8:
                prefix += chunk[: 8 - len(prefix)]
            digest.update(chunk)
            size += len(chunk)
    valid = prefix.startswith(b"%PDF-") and size > 8
    return {
        "integrity_status": "valid_pdf_bytes" if valid else "invalid_pdf_bytes",
        "size_bytes": size,
        "sha256": digest.hexdigest(),
    }


def expected_filename(url: str, number) -> str:
    import re
    import urllib.parse
    raw = urllib.parse.unquote((url.split("/")[-1] or "").split("?")[0])
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-").lower() or "bando"
    if not stem.endswith(".pdf"):
        stem += ".pdf"
    return f"{number}-{stem[:80]}"


def main() -> None:
    payload = json.loads((DATA / "conservatori.json").read_text(encoding="utf-8"))
    entries = []
    referenced = set()
    for item in payload.get("items", []):
        paths = []
        if item.get("pdf_local"):
            paths.append(item["pdf_local"])
        paths.extend(item.get("pdf_locals") or [])
        for relative in paths:
            path = ROOT / relative
            referenced.add(path.resolve())
            integrity = inspect_pdf(path)
            original_url = next((url for url in item.get("documents", []) if expected_filename(url, item.get("number")) == path.name), None)
            entries.append({
                "institution": item.get("name") or item.get("institution") or item.get("number"),
                "source_record_number": item.get("number"),
                "local_path": relative,
                "source_url": original_url,
                **integrity,
                "publisher_signature_status": "not_verified",
                "verification_note": "SHA-256 verifies byte consistency only; publisher identity/signature has not been verified.",
            })
    orphans = []
    if PDF_DIR.exists():
        for path in sorted(PDF_DIR.glob("*.pdf")):
            if path.resolve() not in referenced:
                orphans.append({
                    "local_path": path.relative_to(ROOT).as_posix(),
                    **inspect_pdf(path),
                    "publisher_signature_status": "not_verified",
                    "verification_note": "Unreferenced local PDF retained for review; no source identity inferred from filename.",
                })
    result = {
        "generated_at": datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds"),
        "algorithm": "SHA-256",
        "purpose": "Local byte-integrity manifest for mirrored PDF files",
        "publisher_signature_verification": "not_implemented",
        "referenced_pdf_count": len(entries),
        "valid_pdf_count": sum(entry["integrity_status"] == "valid_pdf_bytes" for entry in entries),
        "invalid_or_missing_pdf_count": sum(entry["integrity_status"] != "valid_pdf_bytes" for entry in entries),
        "unreferenced_pdf_count": len(orphans),
        "files": entries,
        "unreferenced_files": orphans,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "referenced_pdf_count", "valid_pdf_count", "invalid_or_missing_pdf_count",
        "unreferenced_pdf_count", "publisher_signature_verification"
    )}, ensure_ascii=False))


if __name__ == "__main__":
    main()
