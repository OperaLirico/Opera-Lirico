#!/usr/bin/env python3
"""Read-only PDF signature inventory. Never upgrades publisher identity status."""
from __future__ import annotations
import hashlib, json, re, subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / ".github" / "audits" / "pdf-integrity-manifest.json"
OUT_JSON = ROOT / ".github" / "audits" / "pdf-signature-audit-latest.json"
OUT_MD = ROOT / ".github" / "audits" / "pdf-signature-audit-latest.md"

def _field(block: str, name: str) -> str | None:
    match = re.search(rf"^\s*(?:-\s*)?{re.escape(name)}:\s*(.*?)\s*$", block, re.I | re.M)
    return match.group(1).strip() if match else None

def _classify_signature_validation(value: str | None) -> str:
    if not value: return "not_reported"
    lowered = value.lower()
    if "signature is valid" in lowered: return "valid"
    if "signature is invalid" in lowered or "validation failed" in lowered: return "invalid"
    return "inconclusive"

def _classify_certificate_validation(value: str | None) -> str:
    if not value: return "not_reported"
    lowered = value.lower()
    if "certificate is trusted" in lowered: return "trusted"
    if any(token in lowered for token in ("not trusted", "unknown", "untrusted", "unable to build", "not valid")):
        return "untrusted_or_unknown"
    return "inconclusive"

def parse_pdfsig_output(output: str) -> dict:
    starts = list(re.finditer(r"^\s*Signature #(\d+):", output, re.I | re.M))
    if not starts:
        if re.search(r"does not contain any signatures|no signatures", output, re.I):
            return {"signature_presence": "not_detected", "signatures": []}
        return {"signature_presence": "inconclusive", "signatures": []}
    signatures = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(output)
        block = output[match.start():end]
        sig_validation = _field(block, "Signature Validation")
        cert_validation = _field(block, "Certificate Validation")
        signatures.append({
            "signature_number": int(match.group(1)),
            "field_name": _field(block, "Signature Field Name"),
            "signer_common_name": _field(block, "Signer Certificate Common Name"),
            "signer_distinguished_name": _field(block, "Signer full Distinguished Name"),
            "signing_time": _field(block, "Signing Time"),
            "hash_algorithm": _field(block, "Signing Hash Algorithm"),
            "signature_type": _field(block, "Signature Type"),
            "signature_integrity_status": _classify_signature_validation(sig_validation),
            "signature_validation_text": sig_validation,
            "certificate_trust_status": _classify_certificate_validation(cert_validation),
            "certificate_validation_text": cert_validation,
            "publisher_identity_status": "not_verified",
        })
    return {"signature_presence": "present", "signatures": signatures}

def classify_inspection_status(return_code: int, parsed: dict) -> str:
    presence = parsed.get("signature_presence")
    if presence == "not_detected":
        return "success_no_signature"
    if presence == "present":
        if all(item.get("signature_validation_text") for item in parsed.get("signatures", [])):
            return "success"
        return "inconclusive"
    return "tool_error" if return_code != 0 else "inconclusive"


def inspect_pdf(entry: dict) -> dict:
    relative = entry.get("local_path", "")
    path = (ROOT / relative).resolve()
    base = {
        "local_path": relative,
        "source_url": entry.get("source_url"),
        "manifest_sha256": entry.get("sha256"),
        "manifest_integrity_status": entry.get("integrity_status"),
        "publisher_identity_status": "not_verified",
    }
    if not path.is_relative_to(ROOT) or not path.is_file():
        return {**base, "inspection_status": "missing_or_invalid_path", "signature_presence": "not_inspected", "signatures": []}
    try:
        proc = subprocess.run(["pdfsig", str(path)], capture_output=True, text=True, timeout=60, check=False)
    except FileNotFoundError:
        return {**base, "inspection_status": "pdfsig_unavailable", "signature_presence": "not_inspected", "signatures": []}
    except subprocess.TimeoutExpired:
        return {**base, "inspection_status": "timeout", "signature_presence": "not_inspected", "signatures": []}
    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    parsed = parse_pdfsig_output(output)
    return {**base, "inspection_status": classify_inspection_status(proc.returncode, parsed),
            "return_code": proc.returncode, **parsed}

def build_report() -> dict:
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    results = [inspect_pdf(entry) for entry in manifest.get("files", [])]
    present = [item for item in results if item.get("signature_presence") == "present"]
    return {
        "generated_at": datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds"),
        "tool": "Poppler pdfsig",
        "manifest_path": str(MANIFEST.relative_to(ROOT)),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "file_count": len(results),
        "inspection_error_count": sum(item.get("inspection_status") in {"tool_error", "pdfsig_unavailable", "timeout", "missing_or_invalid_path"} for item in results),
        "inconclusive_inspection_count": sum(item.get("inspection_status") == "inconclusive" for item in results),
        "signature_present_file_count": len(present),
        "no_signature_detected_file_count": sum(item.get("signature_presence") == "not_detected" for item in results),
        "signature_count": sum(len(item.get("signatures", [])) for item in results),
        "cryptographically_valid_signature_count": sum(sig.get("signature_integrity_status") == "valid" for item in results for sig in item.get("signatures", [])),
        "invalid_signature_count": sum(sig.get("signature_integrity_status") == "invalid" for item in results for sig in item.get("signatures", [])),
        "inconclusive_signature_count": sum(sig.get("signature_integrity_status") == "inconclusive" for item in results for sig in item.get("signatures", [])),
        "trusted_certificate_count": sum(sig.get("certificate_trust_status") == "trusted" for item in results for sig in item.get("signatures", [])),
        "untrusted_or_unknown_certificate_count": sum(sig.get("certificate_trust_status") == "untrusted_or_unknown" for item in results for sig in item.get("signatures", [])),
        "publisher_identity_verified_count": 0,
        "important_limitation": "Signature presence, cryptographic integrity and certificate trust are separate. No certificate subject is mapped to an official institution; publisher identity remains not_verified.",
        "files": results,
    }

def render_markdown(report: dict) -> str:
    lines = [
        "# PDF signature evidence audit", "",
        f"- Generated: {report['generated_at']}",
        f"- Tool: {report['tool']}",
        f"- Files inspected: {report['file_count']}",
        f"- Files with signature fields: {report['signature_present_file_count']}",
        f"- Files with no detected signature: {report['no_signature_detected_file_count']}",
        f"- Inspection errors: {report['inspection_error_count']}",
        f"- Inconclusive inspections: {report['inconclusive_inspection_count']}",
        f"- Signature instances: {report['signature_count']}",
        f"- Cryptographically valid signatures reported: {report['cryptographically_valid_signature_count']}",
        f"- Invalid signatures reported: {report['invalid_signature_count']}",
        f"- Trusted certificates reported: {report['trusted_certificate_count']}",
        f"- Untrusted/unknown certificates reported: {report['untrusted_or_unknown_certificate_count']}",
        "- Publisher identities verified: 0", "",
        "> Signature presence, signature integrity, certificate trust and publisher identity are separate claims. This audit does not map signer certificates to official institutions. No opportunity status or publisher_signature_status is changed.",
        "", "| PDF | Signature presence | Signature integrity | Certificate trust | Publisher identity |",
        "|---|---|---|---|---|",
    ]
    for item in report["files"]:
        signatures = item.get("signatures", [])
        if not signatures:
            lines.append(f"| {item['local_path']} | {item.get('signature_presence', 'not_inspected')} | — | — | not_verified |")
        else:
            for sig in signatures:
                lines.append(f"| {item['local_path']} | present | {sig['signature_integrity_status']} | {sig['certificate_trust_status']} | not_verified |")
    lines.extend(["", f"Manifest SHA-256: {report['manifest_sha256']}", ""])
    return "\n".join(lines)

def main() -> None:
    report = build_report()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))

if __name__ == "__main__":
    main()
