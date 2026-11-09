#!/usr/bin/env python3
"""Run the conservatory collector, retrying the fetch and keeping the last good copy.

Three problems show up in practice:

* Conservatory sites time out often. One run loses Turin, the next loses Genoa,
  so a single attempt leaves visible holes in the board.
* A failed run therefore must not delete what a previous run already read.
* Most schools publish the real dates inside a PDF bando, so a page that only
  says "scarica il bando" leaves the card with a filename and no facts.

So: retry at the fetcher boundary, keep the last good snapshot when a site is
unreachable, and read the official bando PDF to recover the dates and
requirements the HTML never spelled out.
"""

from __future__ import annotations

import io
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path

try:  # the workflow installs pypdf; a missing reader must not break the run
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional dependency
    PdfReader = None

from scrapling.fetchers import Fetcher as RawFetcher

import scrape_conservatori as core

# Announcements that reach the admission page but are not admission deadlines:
# grants, research doctorates, seminars, staff shortlists, "admitted students" lists.
OTHER_NOTICE = re.compile(
    r"assegnazion|dottorat|seminari|individuazione di|graduator|ammess|borsa di studio|"
    r"masterclass|rassegna|stagione concertistica",
    re.IGNORECASE,
)
# Text that only looks like a date because it sits next to the word "iscrizione".
PDF_NOISE = re.compile(
    r"fuori corso|anno accademico successivo|tassa|contributo|visto il|vista la|considerato|"
    r"il presente decreto|modulistica|documento di identit|marca da bollo",
    re.IGNORECASE,
)
# Rank the PDFs: a bando carries dates, an academic calendar or a study plan does not.
PDF_BONUS = [
    (re.compile(r"bando|ammissioni?-", re.IGNORECASE), 3),
    (re.compile(r"ammission", re.IGNORECASE), 2),
    (re.compile(r"prorog|calendario[-_ ]?ammissioni|calendario[-_ ]?prove", re.IGNORECASE), 2),
    (re.compile(r"requisiti|programma[-_ ]?ammissione", re.IGNORECASE), 1),
]
PDF_PENALTY = re.compile(
    r"calendario[-_ ]?accademico|piano[-_ ]?di[-_ ]?studi|programma[-_ ]?studio|"
    r"english|inglese|curriculum|informativa|privacy",
    re.IGNORECASE,
)
FILE_NAME = re.compile(r"\.pdf\b|^[\w\-.%()]+$")
DATE_IN_LINE = re.compile(r"\b20\d{2}\b|\b\d{1,2}\s*(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)", re.IGNORECASE)

ATTEMPTS = 2
TIMEOUT = 25
MAX_PDF_BYTES = 12 * 1024 * 1024
MAX_PDF_PAGES = 5
PDF_BUDGET = 30  # ~2 per institution, keeps the job inside a few minutes
DATA = Path(__file__).resolve().parent / "data" / "conservatori.json"


HARD_DEADLINE = 40  # seconds; covers a stalled TLS handshake the curl timeout misses
# One worker per in-flight request: the collector already fans out over
# ``core.WORKERS`` threads, and a single-slot pool would serialise them again.
POOL = ThreadPoolExecutor(max_workers=core.WORKERS)


def _attempt(url: str):
    # ``core.Fetcher`` is replaced by RetryingFetcher below; submitting *that* would
    # re-enter this pool and deadlock, so the raw client is captured once here.
    return POOL.submit(RawFetcher.get, url, timeout=TIMEOUT, retries=0)


class RetryingFetcher:
    @staticmethod
    def get(url: str, **_kwargs):
        last_error: Exception | None = None
        for attempt in range(1, ATTEMPTS + 1):
            try:
                # A site can accept the connection and then stall past curl's
                # own timeout; the future deadline keeps the whole run bounded.
                return _attempt(url).result(timeout=HARD_DEADLINE)
            except FutureTimeout:
                raise TimeoutError(f"no response within {HARD_DEADLINE}s: {url}")
            except Exception as exc:  # curl timeouts, TLS resets, empty replies
                last_error = exc
                if attempt < ATTEMPTS:
                    time.sleep(3 * attempt)
        raise last_error if last_error else RuntimeError("fetch failed")


def snapshots() -> dict[int, dict]:
    """Successful records already in the repository, keyed by institution number."""
    if not DATA.exists():
        return {}
    try:
        payload = json.loads(DATA.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    keep: dict[int, dict] = {}
    for item in payload.get("items", []):
        if item.get("status") == "ok":
            keep[item.get("number")] = item
    return keep


def backfill(previous: dict[int, dict]) -> None:
    if not previous or not DATA.exists():
        return
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    replaced = 0
    for item in payload.get("items", []):
        if item.get("status") == "ok":
            continue
        old = previous.get(item.get("number"))
        if not old:
            continue
        for field in ("deadline_lines", "exam_dates", "requirements", "documents", "title", "fallback_lines"):
            if old.get(field):
                item[field] = old[field]
        item["status"] = "ok"
        item["cached"] = True
        item["checked_at"] = old.get("checked_at")
        item["note"] = "本次未连通，显示上一次成功读取的内容"
        replaced += 1
    if replaced:
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Kept the previous snapshot for {replaced} institution(s)")


def drop_other_notices() -> None:
    """Strip scholarship/doctorate/seminar notices that slipped into the timeline fields."""
    if not DATA.exists():
        return
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    removed = 0
    for item in payload.get("items", []):
        for field in ("deadline_lines", "exam_dates", "requirements"):
            kept = [line for line in item.get(field) or [] if not OTHER_NOTICE.search(line)]
            if len(kept) != len(item.get(field) or []):
                removed += len(item.get(field) or []) - len(kept)
                item[field] = kept
    if removed:
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Dropped {removed} non-admission notice(s)")


def drop_file_names() -> None:
    """A link label such as BANDO_2026.pdf is a document, not a sentence."""
    if not DATA.exists():
        return
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    removed = 0
    for item in payload.get("items", []):
        for field in ("deadline_lines", "exam_dates", "requirements"):
            kept = [line for line in item.get(field) or [] if not FILE_NAME.search(line.strip())]
            if len(kept) != len(item.get(field) or []):
                removed += len(item.get(field) or []) - len(kept)
                item[field] = kept
    if removed:
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Dropped {removed} file-name line(s)")


def pdf_rank(url: str) -> int:
    tail = url.rsplit("/", 1)[-1]
    score = 0
    for pattern, weight in PDF_BONUS:
        if pattern.search(tail):
            score += weight
    if PDF_PENALTY.search(tail):
        score -= 2
    return score


def pdf_read(url: str) -> list[str]:
    """Download a bando and turn its first pages into clean text lines."""
    if PdfReader is None:
        return []
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "leo-conservatori-bot/1.0"})
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            data = response.read(MAX_PDF_BYTES + 1)
        if len(data) > MAX_PDF_BYTES:
            return []
        text = "\n".join((page.extract_text() or "") for page in PdfReader(io.BytesIO(data)).pages[:MAX_PDF_PAGES])
    except Exception:
        return []
    lines = [core.clean_line(line) for line in text.splitlines()]
    return [line for line in lines if len(line) > 12 and not PDF_NOISE.search(line)]


def fill_from_pdfs(payload: dict) -> None:
    """Give the card the dates that only exist inside the official bando."""
    if PdfReader is None:
        print("pypdf not installed, skipping PDF reading")
        return
    budget = PDF_BUDGET
    filled = 0
    for item in payload.get("items", []):
        if item.get("status") != "ok":
            continue
        documents = item.get("documents") or []
        if not documents:
            continue
        if item.get("deadline_lines") and item.get("exam_dates"):
            continue
        ranked = [url for url in sorted(documents, key=pdf_rank, reverse=True) if pdf_rank(url) > 0][:2]
        for url in ranked:
            if budget <= 0:
                break
            budget -= 1
            lines = pdf_read(url)
            if not lines:
                continue
            deadlines, dates, requirements = core.signals(lines)
            added = False
            if not item.get("deadline_lines"):
                keep = [line for line in deadlines if DATE_IN_LINE.search(line) and not PDF_NOISE.search(line)][:2]
                if keep:
                    item["deadline_lines"] = keep
                    added = True
            if not item.get("exam_dates"):
                keep = [
                    line
                    for line in dates
                    if DATE_IN_LINE.search(line)
                    and re.search(r"ammission|prova|esame|audizion|colloquio", line, re.IGNORECASE)
                ][:2]
                if keep:
                    item["exam_dates"] = keep
                    added = True
            if not item.get("requirements"):
                keep = requirements[:2]
                if keep:
                    item["requirements"] = keep
                    added = True
            if added:
                item["pdf_checked"] = url
                filled += 1
                break
    print(f"Read {PDF_BUDGET - budget} bando PDF(s), enriched {filled} institution(s)")


def save(payload: dict) -> None:
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    previous = snapshots()
    core.Fetcher = RetryingFetcher
    core.main()
    backfill(previous)
    drop_other_notices()
    drop_file_names()
    if DATA.exists():
        payload = json.loads(DATA.read_text(encoding="utf-8"))
        fill_from_pdfs(payload)
        save(payload)
