#!/usr/bin/env python3
"""Create a Buttondown draft from a local markdown file.

Used for one-off announcements and single articles, where the weekly digest
generator is the wrong size of tool. Never sends: only POSTs a draft.

The file may start with a level-1 heading; that heading becomes the subject
unless --subject is given.

    python content_engine/buttondown_draft.py content/newsletter-announcement.md
    python content_engine/buttondown_draft.py draft.md --email-type public --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.buttondown.com/v1/emails"


def load_source(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    subject = ""
    if text.startswith("# "):
        first, _, rest = text.partition("\n")
        subject = first[2:].strip()
        text = rest.strip()
    return subject, text


def slugify(subject: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    ascii_part = re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")
    match = re.search(r"(20\d{2})-(\d{2})-(\d{2})", subject)
    date_part = "-".join(match.groups()) if match else ""
    stem = ascii_part or "draft"
    if date_part:
        # Avoid opera-lirico-2026-11-15-2026-11-15 when the subject already carries the date.
        stem = stem.replace("-" + date_part, "").strip("-")
        return f"{stem}-{date_part}" if stem else date_part
    return stem[:70]


def build_payload(subject: str, body: str, args: argparse.Namespace) -> dict:
    return {
        "subject": subject,
        "body": body,
        "status": "draft",
        "email_type": args.email_type,
        "archival_mode": args.archival_mode,
        "slug": slugify(subject, args.slug),
    }


def post(payload: dict) -> tuple[int, str]:
    key = os.environ.get("BUTTONDOWN_API_KEY", "")
    if not key:
        raise SystemExit("BUTTONDOWN_API_KEY is not set; refusing to create a draft")
    request = urllib.request.Request(
        API,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Authorization": "Token " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Buttondown draft from a markdown file")
    parser.add_argument("source")
    parser.add_argument("--subject", default="")
    parser.add_argument("--slug", default=None)
    parser.add_argument("--email-type", default="private", choices=["private", "public", "premium", "free"])
    parser.add_argument("--archival-mode", default="disabled", choices=["disabled", "enabled"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    path = Path(args.source)
    file_subject, body = load_source(path)
    subject = args.subject or file_subject
    if not subject:
        raise SystemExit("no subject: put a '# heading' at the top of the file or pass --subject")
    if not body:
        raise SystemExit("empty body")

    payload = build_payload(subject, body, args)
    print(f"subject: {subject}")
    print(f"slug: {payload['slug']}")
    print(f"type: {payload['email_type']} / archival {payload['archival_mode']} / status draft")
    print(f"body: {len(body)} chars, {body.count(chr(10)) + 1} lines")

    if args.dry_run:
        print("dry run: no request sent")
        return 0

    status, raw = post(payload)
    if status not in (200, 201):
        print(f"failed: HTTP {status}", file=sys.stderr)
        print(raw[:400], file=sys.stderr)
        return 1
    data = json.loads(raw)
    print(f"draft created: id={data.get('id')} status={data.get('status')} slug={data.get('slug')}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(
                f"- draft `{data.get('slug')}` created (id `{data.get('id')}`, "
                f"status `{data.get('status')}`, type `{data.get('email_type')}`)\n"
            )
            handle.write("- nothing was sent; review in Buttondown and press send there\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
