#!/usr/bin/env python3
"""Scrape Italian state conservatories for admission dates and requirements.

The daily job already watches theatres and competitions in ``scrape_sources.py``.
Conservatories are a different animal: 60+ AFAM institutions, every one with its
own site structure, and the useful information is not an audition notice but
the admission calendar — application window, exam session, language and
programme requirements.

So they get their own collector and their own data file (``data/conservatori.json``),
and each institution is pinned to the page that actually carries admission
information rather than to its home page. Extracts keep the official wording
(verbatim), plus links to the official PDFs, because the full per-instrument
exam programme almost always lives in a PDF.
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from scrapling.fetchers import Fetcher

# (number, Chinese city label, institution, admission page)
CONSERVATORIES = [
    (1, "都灵", "Conservatorio Giuseppe Verdi", "https://www.conservatoriotorino.eu/segreteria/ammissioni/"),
    (2, "米兰", "Conservatorio Giuseppe Verdi", "https://www.consmi.it/ammissioni/"),
    (3, "罗马", "Conservatorio Santa Cecilia", "https://conservatoriosantacecilia.it/triennio-piani-di-studio-e-ammissione/"),
    (4, "博洛尼亚", "Conservatorio G.B. Martini", "https://consbo.it/iscriviti/ammissioni/"),
    (5, "博洛尼亚", "Martini — 学年日程与截止", "https://consbo.it/didattica/manifesto-degli-studi-tasse-e-regolamenti/a-a-2026-2027/"),
    (6, "威尼斯", "Conservatorio Benedetto Marcello", "https://www.conservatoriovenezia.eu/ammissioni-e-immatricolazioni/"),
    (7, "那不勒斯", "Conservatorio San Pietro a Majella", "https://www.sanpietroamajella.it/calendario-ammissioni-a-a-26-27/"),
    (8, "巴里", "Conservatorio Niccolò Piccinni", "https://www.consba.it/it/6584/ammissioni"),
    (9, "佛罗伦萨", "Conservatorio Luigi Cherubini", "https://www.consfi.it/calendario-corsi/"),
    (10, "布雷西亚", "Conservatorio Luca Marenzio", "https://www.consbs.it/ammissioni/"),
    (11, "墨西拿", "Conservatorio Arcangelo Corelli", "https://www.consme.it/"),
    (12, "乌迪内", "Conservatorio Jacopo Tomadini", "https://www.conservatorio.udine.it/didattica/ammissione-e-iscrizioni.html"),
    (13, "帕多瓦", "Conservatorio Cesare Pollini", "https://www.conservatoriopollini.it/site/it/didattica-iscrizioni/"),
    (14, "热那亚", "Conservatorio Niccolò Paganini", "https://www.conspaganini.it/"),
]

ADMISSION_KEYWORDS = re.compile(
    r"ammission|iscrizion|immatricol|bando|graduatori|scadenz|entro il|termine|"
    r"prorog|colloquio|esame|prova|programma|triennio|biennio|propedeutic|afam|isidata",
    re.IGNORECASE,
)
REQUIREMENT_HINTS = re.compile(
    r"programma (?:del|di|d'esame)|prova (?:pratica|teorica|di)|colloquio|lingua italiana|"
    r"titolo di studio|diploma (?:di|accademico)|crediti|requisit|richied|necessari|occorre",
    re.IGNORECASE,
)
DEADLINE_HINTS = re.compile(r"scadenz|entro il|entro|termine|prorog|apert[oa]|chius[oa]|domanda", re.IGNORECASE)
# School pages often drop the year ("dal 11 marzo al 11 aprile") or use day/month pairs.
DATE_SOFT_RE = re.compile(
    r"\b\d{1,2}\s+(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)"
    r"(?:\s+20\d{2})?\b"
    r"|\b\d{1,2}[./]\d{1,2}(?:[./]20\d{2})?\b",
    re.IGNORECASE,
)
DOC_HINTS = re.compile(r"ammission|calendario|programma|guida|bando|iscrizion|immatricol|prova", re.IGNORECASE)
NOISE = re.compile(r"^(cookie|privacy|home|contatti|news|eventi|sitemap|accedi|login)\b", re.IGNORECASE)


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def fetch_page(url: str) -> tuple[int, str, list[str], object]:
    response = Fetcher.get(url, timeout=35, retries=0)
    status = getattr(response, "status", 0) or 0
    title = clean_line(response.css("title::text").get() or "")
    text = response.get_all_text(separator="\n") or ""
    lines = [clean_line(line) for line in text.splitlines()]
    return status, title, [line for line in lines if line], response


def extract_deadlines(lines: list[str], limit: int = 6) -> list[str]:
    out: list[str] = []
    for line in lines:
        if NOISE.match(line) or len(line) < 20:
            continue
        if not DEADLINE_HINTS.search(line):
            continue
        if not DATE_SOFT_RE.search(line) and not re.search(r"prorog|riapert", line, re.IGNORECASE):
            continue
        out.append(line)
        if len(out) >= limit:
            break
    return out


def extract_dates(lines: list[str], limit: int = 8) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        if NOISE.match(line) or not DATE_SOFT_RE.search(line) or not ADMISSION_KEYWORDS.search(line):
            continue
        key = DATE_SOFT_RE.findall(line)[0].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(line)
        if len(out) >= limit:
            break
    return out


def extract_requirements(lines: list[str], limit: int = 8) -> list[str]:
    out: list[str] = []
    for line in lines:
        if NOISE.match(line) or not REQUIREMENT_HINTS.search(line):
            continue
        if not 30 <= len(line) <= 320:
            continue
        if DATE_SOFT_RE.search(line) and not re.search(r"prova|esame|colloquio", line, re.IGNORECASE):
            continue
        out.append(line)
        if len(out) >= limit:
            break
    return out


def collect_documents(response, base_url: str, limit: int = 6) -> list[str]:
    """Official PDFs: the exam calendar and the per-instrument programmes."""
    try:
        hrefs = response.css("a::attr(href)").getall()
    except Exception:
        return []
    ranked: list[tuple[int, str]] = []
    seen: set[str] = set()
    for href in hrefs:
        if not href:
            continue
        absolute = urljoin(base_url, href.strip())
        if not re.search(r"\.pdf($|\?)", absolute, re.IGNORECASE) or absolute in seen:
            continue
        seen.add(absolute)
        ranked.append((0 if DOC_HINTS.search(absolute) else 1, absolute))
    ranked.sort()
    return [url for _, url in ranked[:limit]]


def main() -> None:
    out_dir = Path(__file__).resolve().parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")
    items: list[dict] = []

    for number, city, school, url in CONSERVATORIES:
        item = {
            "number": number,
            "city": city,
            "school": school,
            "url": url,
            "checked_at": checked_at,
            "status": "error",
            "http_status": None,
            "title": "",
            "deadline_lines": [],
            "exam_dates": [],
            "requirements": [],
            "documents": [],
            "error": None,
        }
        try:
            status, title, lines, response = fetch_page(url)
            item["http_status"] = status
            item["title"] = title
            item["status"] = "ok" if status and status < 400 else "http_error"
            item["deadline_lines"] = extract_deadlines(lines)
            item["exam_dates"] = extract_dates(lines)
            item["requirements"] = extract_requirements(lines)
            item["documents"] = collect_documents(response, url)
        except Exception as exc:  # One unreachable institute must not stop the batch.
            item["error"] = f"{type(exc).__name__}: {exc}"
        items.append(item)
        print(
            f"[{number:02d}/{len(CONSERVATORIES):02d}] {item['status']} {item['http_status']} "
            f"{city} — deadlines={len(item['deadline_lines'])} dates={len(item['exam_dates'])} "
            f"req={len(item['requirements'])} pdf={len(item['documents'])}",
            flush=True,
        )
        time.sleep(1.2)

    path = out_dir / "conservatori.json"
    path.write_text(
        json.dumps({"generated_at": checked_at, "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    readable = sum(1 for item in items if item["status"] == "ok")
    print(f"Saved {path} ({readable}/{len(items)} readable)")


if __name__ == "__main__":
    main()
