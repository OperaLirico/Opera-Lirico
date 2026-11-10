#!/usr/bin/env python3
"""Extract reviewable candidate facts from a local Italian conservatory PDF.

This is an isolated experiment. It does not edit the site's data files and does
not publish anything. Every extracted fact must be checked against the source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_PAGES = 20

DATE_RE = re.compile(
    r"\b(?:\d{1,2}[./-]\d{1,2}[./-](?:20)?\d{2}|"
    r"\d{1,2}\s+(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|"
    r"agosto|settembre|ottobre|novembre|dicembre)\s+20\d{2})\b",
    re.IGNORECASE,
)
DEADLINE_RE = re.compile(
    r"scadenza|entro il|termine (?:ultimo )?(?:per|di)|"
    r"presentazione delle domande|domanda di ammissione|iscrizioni? entro|"
    r"domande entro|ore \d{1,2}[.:]\d{2}",
    re.IGNORECASE,
)
AGE_RE = re.compile(
    r"(?:età|eta|anni compiuti|non (?:deve )?aver compiuto|under)\s*"
    r"(?:massima|minima|di|inferiore a|superiore a)?\s*\d{1,2}\s*anni?",
    re.IGNORECASE,
)
VOICE_RE = re.compile(
    r"\b(soprano|mezzosoprano|mezzo[- ]soprano|contralto|"
    r"controtenore|tenore|baritono|basso|voci? (?:femminili|maschili))\b",
    re.IGNORECASE,
)
REQUIREMENT_RE = re.compile(
    r"repertorio|programma musicale|programma d'esame|programma di esame|"
    r"brani|arie|audizione|prova pratica|titolo di studio|diploma|"
    r"documentazione richiesta|requisiti",
    re.IGNORECASE,
)


def clean_lines(markdown: str) -> list[str]:
    """Normalize markdown into useful, non-empty evidence lines."""
    lines = []
    for raw in markdown.splitlines():
        line = re.sub(r"^\s{0,3}(?:#{1,6}\s*|[-*+]\s+|\d+[.)]\s+)", "", raw)
        line = re.sub(r"\s+", " ", line).strip(" \t|")
        if len(line) >= 8:
            lines.append(line[:600])
    return lines


def unique_matches(lines: Iterable[str], pattern: re.Pattern[str], limit: int = 12) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for line in lines:
        if pattern.search(line):
            key = line.casefold()
            if key not in seen:
                seen.add(key)
                found.append(line)
                if len(found) >= limit:
                    break
    return found


def extract_candidates(markdown: str) -> dict:
    """Return evidence snippets, not asserted facts."""
    lines = clean_lines(markdown)
    deadline_lines = [
        line for line in lines
        if DEADLINE_RE.search(line) and (DATE_RE.search(line) or "ore " in line.lower())
    ]
    return {
        "deadline_candidates": unique_matches(deadline_lines, re.compile(r".+"), 10),
        "age_limit_candidates": unique_matches(lines, AGE_RE, 10),
        "voice_type_candidates": unique_matches(lines, VOICE_RE, 20),
        "requirement_candidates": unique_matches(lines, REQUIREMENT_RE, 20),
        "date_candidates": unique_matches(lines, DATE_RE, 20),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def convert_pdf(path: Path) -> tuple[str, str]:
    """Convert with Docling; import lazily so text extraction tests need no ML stack."""
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:
        raise RuntimeError(
            "Docling non è installato. Esegui: "
            "python -m pip install -r tools/pdf_parser/requirements.txt"
        ) from exc

    converter = DocumentConverter()
    result = converter.convert(path, max_num_pages=MAX_PAGES, max_file_size=MAX_FILE_BYTES)
    status = getattr(result.status, "value", str(result.status))
    if status not in {"success", "partial_success"}:
        details = [
            getattr(error, "error_message", str(error))
            for error in (getattr(result, "errors", None) or [])
        ]
        raise RuntimeError(f"Docling conversion status: {status}. {'; '.join(details)}")
    return result.document.export_to_markdown(), status


def build_record(path: Path, markdown: str, conversion_status: str) -> dict:
    return {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_file": path.name,
        "source_sha256": sha256_file(path),
        "parser": "docling",
        "conversion_status": conversion_status,
        "verification_status": "pending_manual_review",
        "is_verified": False,
        "review_warning": (
            "These are candidate snippets, not verified admission facts. "
            "Check every item against the original official PDF."
        ),
        "candidates": extract_candidates(markdown),
    }


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("pdf", type=Path, help="Path to a locally downloaded official PDF")
    cli.add_argument("--output", type=Path, help="JSON output path (default: <pdf>.candidates.json)")
    cli.add_argument("--include-markdown", action="store_true", help="Also include converted Markdown in JSON")
    args = cli.parse_args()

    path = args.pdf.expanduser().resolve()
    if not path.is_file():
        cli.error(f"PDF file not found: {path}")
    if path.suffix.lower() != ".pdf":
        cli.error("Input must be a .pdf file")
    size = path.stat().st_size
    if size <= 0 or size > MAX_FILE_BYTES:
        cli.error(f"PDF size must be between 1 byte and {MAX_FILE_BYTES} bytes")

    try:
        markdown, status = convert_pdf(path)
        record = build_record(path, markdown, status)
        if args.include_markdown:
            record["markdown"] = markdown
        output = args.output or path.with_suffix(".candidates.json")
        output = output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        temp = output.with_suffix(output.suffix + ".tmp")
        temp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp.replace(output)
    except Exception as exc:
        print(f"PDF parsing failed: {exc}", file=sys.stderr)
        return 1

    print(f"Saved review candidates: {output}")
    print("Status: pending_manual_review (nothing has been published)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
