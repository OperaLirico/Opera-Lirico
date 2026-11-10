#!/usr/bin/env python3
"""Isolated Docling evaluation over verified local PDF mirrors; never publishes data."""
from __future__ import annotations
import hashlib, importlib.metadata, json, re, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / ".github" / "audits" / "pdf-integrity-manifest.json"
OUTPUT = ROOT / "artifacts" / "docling-evaluation"
SAMPLE_PATHS = [
    "data/pdfs/4-bando-di-ammissione-a.a.-2026-2027.pdf",
    "data/pdfs/11-allegato-a-bando-afam030.pdf",
    "data/pdfs/37-riapertura-termini-bando-ammissione-corso-propedeutico-2026-2027.pdf",
    "data/pdfs/306-bandoaccademialirica_2026_tm.pdf",
    "data/pdfs/307-bando-accademia-tcf_261110.pdf",
]
ROME = ZoneInfo("Europe/Rome")
SIGNALS = {
    "voice_types": re.compile(r"soprano|mezzosoprano|contralto|tenore|baritono|basso|tenor|baritone", re.I),
    "deadline": re.compile(r"scadenz|entro il|termine|deadline|no later than", re.I),
    "dates": re.compile(r"\b(?:\d{1,2}[./-]\d{1,2}[./-]20\d{2}|20\d{2})\b", re.I),
    "fees": re.compile(r"quota|tassa|contributo|euro|€", re.I),
    "eligibility": re.compile(r"età|eta|anni|nato|nata|requisit|partecipare|eligib", re.I),
    "application": re.compile(r"domanda|iscrizion|candidatura|application|modulo", re.I),
    "repertoire": re.compile(r"repertorio|aria|arie|spartit|partitura|repertoire", re.I),
}

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def collect_page_text(document) -> dict[int, str]:
    pages: dict[int, list[str]] = {}
    for item, _level in document.iterate_items():
        value = getattr(item, "text", "")
        if not isinstance(value, str) or not value.strip():
            continue
        for provenance in getattr(item, "prov", None) or []:
            page_no = getattr(provenance, "page_no", None)
            if isinstance(page_no, int):
                pages.setdefault(page_no, []).append(value.strip())
    return {number: "\n".join(parts) for number, parts in pages.items()}

def evidence_for_pages(page_text: dict[int, str]) -> list[dict]:
    evidence = []
    for page_no, text in sorted(page_text.items()):
        for signal, pattern in SIGNALS.items():
            match = pattern.search(text)
            if match:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 180)
                excerpt = re.sub(r"\s+", " ", text[start:end]).strip()
                evidence.append({"signal": signal, "page_no": page_no, "excerpt": excerpt[:320]})
    return evidence[:60]

def main() -> int:
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_by_path = {entry["local_path"]: entry for entry in manifest.get("files", [])}
    options = PdfPipelineOptions()
    options.do_ocr = True
    options.do_table_structure = True
    options.enable_remote_services = False
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )
    report = {
        "generated_at": datetime.now(ROME).isoformat(timespec="seconds"),
        "docling_version": importlib.metadata.version("docling"),
        "scope": "Isolated evaluation of local official PDF mirrors; no production writes.",
        "sample_paths": SAMPLE_PATHS,
        "publisher_signature_verification": "not_performed",
        "publication_gate": {"review_status": "pending_manual_review", "is_verified": False,
                             "publication_eligible": False},
        "records": [],
    }
    for relative_path in SAMPLE_PATHS:
        path = ROOT / relative_path
        manifest_entry = manifest_by_path.get(relative_path)
        record = {
            "local_path": relative_path,
            "source_url": manifest_entry.get("source_url") if manifest_entry else None,
            "publisher_signature_status": (
                manifest_entry.get("publisher_signature_status", "not_verified")
                if manifest_entry else "unknown"
            ),
            "status": "not_started",
            "manual_review_required": True,
            "is_verified": False,
            "publication_eligible": False,
        }
        if not manifest_entry or not path.is_file():
            record["status"] = "missing_manifest_entry_or_file"
            report["records"].append(record)
            continue
        actual_hash = sha256_file(path)
        record.update({"size_bytes": path.stat().st_size, "sha256": actual_hash,
                       "manifest_sha256_matches": actual_hash == manifest_entry.get("sha256")})
        if not record["manifest_sha256_matches"]:
            record["status"] = "integrity_mismatch_skipped"
            report["records"].append(record)
            continue
        started = time.perf_counter()
        try:
            result = converter.convert(str(path), raises_on_error=False,
                                       max_num_pages=60, max_file_size=8 * 1024 * 1024)
            record["conversion_status"] = str(result.status)
            record["errors"] = [str(error)[:500] for error in (getattr(result, "errors", None) or [])]
            if result.document is None:
                record["status"] = "conversion_failed"
            else:
                document = result.document
                page_text = collect_page_text(document)
                record.update({
                    "status": "converted",
                    "page_count": len(document.pages),
                    "pages_with_text": len(page_text),
                    "page_text_characters": {str(page): len(text) for page, text in sorted(page_text.items())},
                    "table_count": len(document.tables),
                    "markdown_characters": len(document.export_to_markdown()),
                    "evidence_candidates": evidence_for_pages(page_text),
                    "low_text_pages": [
                        page for page in range(1, len(document.pages) + 1)
                        if len(page_text.get(page, "")) < 40
                    ],
                    "interpretation": "Low text is a review flag, not proof that a page is scanned.",
                })
        except Exception as exc:
            record.update({"status": "conversion_error",
                           "error": f"{type(exc).__name__}: {str(exc)[:500]}"})
        record["runtime_seconds"] = round(time.perf_counter() - started, 2)
        report["records"].append(record)
    (OUTPUT / "docling-evaluation-latest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# Isolated Docling PDF evaluation", "",
        f"- Generated: {report['generated_at']} (Europe/Rome)",
        f"- Docling: {report['docling_version']}",
        f"- Samples: {len(report['records'])}",
        "- Production data changes: none",
        "- Publisher signatures: not verified",
        "- All extracted evidence remains pending manual review and is not publication-eligible.", "",
    ]
    for record in report["records"]:
        lines += [f"## {record['local_path']}", "", f"- Status: {record['status']}",
                  f"- Source: {record.get('source_url')}",
                  f"- SHA-256 matches manifest: {record.get('manifest_sha256_matches')}"]
        if record.get("status") == "converted":
            lines += [
                f"- Pages: {record['page_count']}; pages with text provenance: {record['pages_with_text']}",
                f"- Tables: {record['table_count']}; Markdown characters: {record['markdown_characters']}",
                f"- Runtime: {record['runtime_seconds']}s",
                f"- Low-text pages (review only): {record['low_text_pages']}",
            ]
            for item in record["evidence_candidates"][:20]:
                lines.append(f"- Page {item['page_no']} · {item['signal']}: {item['excerpt']}")
        elif record.get("error"):
            lines.append(f"- Error: {record['error']}")
        lines.append("")
    (OUTPUT / "docling-evaluation-latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "docling_version": report["docling_version"],
        "converted": sum(x["status"] == "converted" for x in report["records"]),
        "failed_or_skipped": sum(x["status"] != "converted" for x in report["records"]),
        "output": str(OUTPUT),
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
