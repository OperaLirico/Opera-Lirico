#!/usr/bin/env python3
"""Scrape Italian AFAM conservatories for admission dates and requirements.

The daily job already watches theatres and competitions in ``scrape_sources.py``.
Conservatories are a different animal: 60+ AFAM institutions, every one with its
own site structure, and the useful information is not an audition notice but
the admission calendar — application window, exam session, language and
programme requirements.

So they get their own collector and their own data file (``data/conservatori.json``).
Two levels of coverage:

* the curated table below, where each institution is pinned to the page that
  carries admission information (or to its home page, from which the admission
  sub-page is found automatically);
* ``data/conservatori_extra.json``, written by ``grow_conservatori.py``, which
  keeps adding institutions discovered from Wikidata over time.

Extracts keep the official wording (verbatim), plus links to the official PDFs,
because the full per-instrument exam programme almost always lives in a PDF.
"""

from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

from scrapling.fetchers import Fetcher

from robots_policy import fetch_page_with_robots

DATA_DIR = Path(__file__).resolve().parent / "data"
EXTRA_PATH = DATA_DIR / "conservatori_extra.json"
OUT_PATH = DATA_DIR / "conservatori.json"

WORKERS = 6  # admission pages are independent; serial crawling took >30 min
# (number, Chinese city label, institution, page — a home page means "find the admission sub-page")
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
    # --- expanded AFAM coverage ---
    (15, "亚历山德里亚", "Conservatorio Antonio Vivaldi", "https://conservatoriovivaldi.it/"),
    (16, "阿韦利诺", "Conservatorio Domenico Cimarosa", "https://conservatoriocimarosa.org/"),
    (17, "博尔扎诺", "Conservatorio Claudio Monteverdi", "https://cons.bz.it/"),
    (18, "坎波巴索", "Conservatorio Lorenzo Perosi", "https://conservatorioperosi.it/"),
    (19, "卡斯泰尔弗兰科", "Conservatorio Agostino Steffani", "https://conscfv.it/"),
    (20, "卡塔尼亚", "Conservatorio Vincenzo Bellini", "https://istitutobellini.it/"),
    (21, "切塞纳", "Conservatorio Bruno Maderna", "https://conservatoriomaderna-cesena.it/"),
    (22, "科森扎", "Conservatorio Stanislao Giacomantonio", "https://portale.conservatoriodicosenza.it/"),
    (23, "库内奥", "Conservatorio Giorgio Federico Ghedini", "https://conservatoriocuneo.it/"),
    (24, "费尔莫", "Conservatorio G.B. Pergolesi", "https://conservatorio.net/"),
    (25, "费拉拉", "Conservatorio Girolamo Frescobaldi", "https://conservatorioferrara.it/"),
    (26, "福贾", "Conservatorio Umberto Giordano", "https://conservatoriofoggia.it/"),
    (27, "弗罗西诺内", "Conservatorio Licinio Refice", "https://conservatorio-frosinone.it/"),
    (28, "拉斯佩齐亚", "Conservatorio Giacomo Puccini", "https://conservatoriopuccini.com/"),
    (29, "拉蒂纳", "Conservatorio Ottorino Respighi", "https://conslatina.it/"),
    (30, "莱切", "Conservatorio Tito Schipa", "https://conservatoriolecce.it/"),
    (31, "卢卡", "Conservatorio Luigi Boccherini", "https://boccherini.it/"),
    (32, "曼托瓦", "Conservatorio Lucio Campiani", "https://conservatoriomantova.com/"),
    (33, "马泰拉", "Conservatorio Egidio Romualdo Duni", "https://conservatoriomatera.it/"),
    (34, "米兰", "Conservatorio G. Verdi（旧域名）", "https://consmilano.it/"),
    (35, "莫诺波利", "Conservatorio Nino Rota", "https://conservatoriodimonopoli.org/"),
    (36, "诺瓦拉", "Conservatorio Guido Cantelli", "https://consno.it/"),
    (37, "巴勒莫", "Conservatorio Alessandro Scarlatti", "https://conservatoriopalermo.it/"),
    (38, "佩鲁贾", "Conservatorio Francesco Morlacchi", "https://conservatorioperugia.it/"),
    (39, "佩萨罗", "Conservatorio Gioachino Rossini", "https://conservatoriorossini.it/"),
    (40, "皮亚琴察", "Conservatorio Giuseppe Nicolini", "https://conservatorionicolini.it/"),
    (41, "波坦察", "Conservatorio Carlo Gesualdo", "https://conservatoriopotenza.it/"),
    (42, "雷焦卡拉布里亚", "Conservatorio Francesco Cilea", "https://conservatoriocilea.it/"),
    (43, "里贝拉", "Conservatorio Arturo Toscanini", "https://conservatoriotoscanini.it/"),
    (44, "罗维戈", "Conservatorio Francesco Venezze", "https://conservatoriorovigo.it/"),
    (45, "萨莱诺", "Conservatorio Giuseppe Martucci", "https://consalerno.com/"),
    (46, "萨萨里", "Conservatorio Luigi Canepa", "https://conservatorio.sassari.it/"),
    (47, "锡耶纳", "Conservatorio Rinaldo Franci", "https://conservatoriosiena.it/"),
    (48, "泰拉莫", "Conservatorio Gaetano Braga", "https://conservatoriobraga.it/"),
    (49, "特拉帕尼", "Conservatorio Antonio Scontrino", "https://conservatorioscontrino.it/"),
    (50, "特伦托", "Conservatorio F.A. Bonporti", "https://conservatorio.tn.it/"),
    (51, "维博瓦伦蒂亚", "Conservatorio Fausto Torrefranca", "https://consvv.it/"),
    (52, "维琴察", "Conservatorio Arrigo Pedrollo", "https://consvi.it/"),
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
# A conservatory site is full of hiring notices and transparency PDFs; they are
# exams for staff posts, not admission for students.
STAFF_NOISE = re.compile(
    r"reclutament|funzionario|personale|borse di studio|borse di mobilita|mobilita|tirocin|"
    r"trasparen|graduatoria (?:definitiva|provvisoria) del personale|titolario|albo|"
    r"lavora con noi|selezione pubblica|assunzion",
    re.IGNORECASE,
)
# Only admission-flavoured lines count: "concerto il 22 ottobre" is not a deadline.
ADMISSION_CONTEXT = re.compile(
    r"ammission|immatricol|iscrizion|preiscrizion|prova (?:d'esame|di ammissione)|triennio|biennio|"
    r"propedeutic|diploma accademic|accademico di (?:primo|secondo|i|ii) livello|"
    r"studenti|corsi di studio|piano di studi",
    re.IGNORECASE,
)
NOISE = re.compile(r"^(cookie|privacy|home|contatti|news|eventi|sitemap|accedi|login)\b", re.IGNORECASE)
# Links worth following from a home page when it carries no admission wording itself.
CANDIDATE_HINTS = re.compile(
    r"ammission|immatricol|iscrizion|bando|graduator|prova|esame|"
    r"offerta-formativa|segreteria|didattica",
    re.IGNORECASE,
)


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def fetch_page(url: str) -> tuple[int, str, list[str], object, dict]:
    response, access = fetch_page_with_robots(
        url, Fetcher.get, timeout=35, retries=0, delay=1.2
    )
    if response is None:
        return 0, "", [], None, access
    status = getattr(response, "status", 0) or 0
    title = clean_line(response.css("title::text").get() or "")
    text = response.get_all_text(separator="\\n") or ""
    lines = [clean_line(line) for line in text.splitlines()]
    return status, title, [line for line in lines if line], response, access


def extract_deadlines(lines: list[str], limit: int = 6) -> list[str]:
    out: list[str] = []
    for line in lines:
        if NOISE.match(line) or len(line) < 20:
            continue
        if not DEADLINE_HINTS.search(line):
            continue
        if not ADMISSION_CONTEXT.search(line) or STAFF_NOISE.search(line):
            continue
        if not DATE_SOFT_RE.search(line) and not re.search(r"prorog|riapert", line, re.IGNORECASE):
            continue
        if line in out:
            continue
        out.append(line)
        if len(out) >= limit:
            break
    return out


def extract_dates(lines: list[str], limit: int = 8) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        if NOISE.match(line) or not DATE_SOFT_RE.search(line):
            continue
        if not ADMISSION_KEYWORDS.search(line) or not ADMISSION_CONTEXT.search(line):
            continue
        if STAFF_NOISE.search(line):
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
        if NOISE.match(line) or not REQUIREMENT_HINTS.search(line) or STAFF_NOISE.search(line):
            continue
        if not ADMISSION_CONTEXT.search(line) and not re.search(
            r"programma (?:del|di|d'esame)|colloquio|lingua italiana|titolo di studio", line, re.IGNORECASE
        ):
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
        if not DOC_HINTS.search(absolute) or STAFF_NOISE.search(absolute):
            continue
        ranked.append((0 if re.search(r"ammission|iscrizion|immatricol|calendario|programma", absolute, re.IGNORECASE) else 1, absolute))
    ranked.sort()
    return [url for _, url in ranked[:limit]]


def is_landing(url: str) -> bool:
    path = urlparse(url).path.rstrip("/")
    return path == "" or path.count("/") == 0


def collect_candidates(response, base_url: str, limit: int = 3) -> list[str]:
    """Admission-ish links on a home page, best first."""
    try:
        hrefs = response.css("a::attr(href)").getall()
    except Exception:
        return []
    host = urlparse(base_url).netloc
    ranked: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for href in hrefs:
        if not href:
            continue
        href = href.strip()
        if href.startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        absolute = urljoin(base_url, href)
        if urlparse(absolute).netloc != host:
            continue
        if re.search(r"\.(pdf|jpg|jpeg|png|zip|doc|docx|xls|xlsx|mp3|mp4)($|\?)", absolute, re.IGNORECASE):
            continue
        if absolute in seen or absolute.rstrip("/") == base_url.rstrip("/"):
            continue
        seen.add(absolute)
        if not CANDIDATE_HINTS.search(absolute):
            continue
        score = 0
        if re.search(r"ammission|immatricol", absolute, re.IGNORECASE):
            score -= 2
        if re.search(r"bando|graduator|prova|esame", absolute, re.IGNORECASE):
            score -= 1
        ranked.append((score, len(urlparse(absolute).path), absolute))
    ranked.sort()
    return [url for _, _, url in ranked[:limit]]


def keyword_lines(lines: list[str], limit: int = 4) -> list[str]:
    """When a page has no calendar, keep its admission wording so the card is not empty."""
    strong = re.compile(r"ammission|iscrizion|immatricol|propedeutic|triennio|biennio|piano di studi", re.IGNORECASE)
    out: list[str] = []
    for pass_no in (0, 1):
        for line in lines:
            if not 30 <= len(line) <= 200 or NOISE.match(line) or STAFF_NOISE.search(line):
                continue
            if line in out:
                continue
            if pass_no == 0 and not strong.search(line):
                continue
            if pass_no == 1 and not ADMISSION_KEYWORDS.search(line):
                continue
            out.append(line)
            if len(out) >= limit:
                break
        if len(out) >= limit:
            break
    return out


def signals(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Date, exam and requirement lines, without the same sentence twice in a row."""
    deadlines = extract_deadlines(lines)
    dates = [line for line in extract_dates(lines) if line not in deadlines]
    requirements = [
        line for line in extract_requirements(lines) if line not in deadlines and line not in dates
    ]
    return deadlines, dates, requirements


def scrape_entry(entry: tuple[int, str, str, str]) -> dict:
    number, city, school, url = entry
    item = {
        "number": number,
        "city": city,
        "school": school,
        "url": url,
        "checked_at": None,
        "status": "error",
        "http_status": None,
        "title": "",
        "deadline_lines": [],
        "exam_dates": [],
        "requirements": [],
        "fallback_lines": [],
        "documents": [],
        "error": None,
        "discovered": False,
    }
    time.sleep(0.4)
    try:
        status, title, lines, response, access = fetch_page(url)
        item["access_policy"] = access
        item["http_status"] = status or access.get("http_status")
        item["title"] = title
        if response is None:
            item["status"] = access.get("status", "robots_policy_unavailable")
            item["error"] = access.get("reason") or access.get("robots_url") or item["status"]
            return item
        item["status"] = "ok" if status and status < 400 else "http_error"
        deadlines, dates, requirements = signals(lines)
        documents = collect_documents(response, url)
        active_lines = lines
        # A home page rarely carries the calendar itself — follow one admission sub-page.
        if is_landing(url) or not (deadlines or dates or requirements):
            for candidate in collect_candidates(response, url):
                try:
                    sub_status, sub_title, sub_lines, sub_response, sub_access = fetch_page(candidate)
                except Exception:
                    continue
                if sub_response is None or not sub_status or sub_status >= 400:
                    continue
                sub_deadlines, sub_dates, sub_requirements = signals(sub_lines)
                gain = len(sub_deadlines) + len(sub_dates) + len(sub_requirements)
                if gain > len(deadlines) + len(dates) + len(requirements):
                    deadlines, dates, requirements = sub_deadlines, sub_dates, sub_requirements
                    documents = collect_documents(sub_response, candidate) or documents
                    item["url"] = candidate
                    item["title"] = clean_line(f"{title} — {sub_title}")[:160]
                    item["discovered"] = True
                    active_lines = sub_lines
                if deadlines and dates:
                    break
        item["deadline_lines"] = deadlines
        item["exam_dates"] = dates
        item["requirements"] = requirements
        item["documents"] = documents
        item["fallback_lines"] = keyword_lines(active_lines)
    except Exception as exc:  # One unreachable institute must not stop the batch.
        item["error"] = f"{type(exc).__name__}: {exc}"
    return item


def load_extra() -> list[tuple[int, str, str, str]]:
    """Institutions discovered by grow_conservatori.py."""
    if not EXTRA_PATH.exists():
        return []
    try:
        payload = json.loads(EXTRA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    out: list[tuple[int, str, str, str]] = []
    for entry in payload.get("items", []):
        url = entry.get("url")
        if not url:
            continue
        out.append((
            int(entry.get("number") or 200 + len(out)),
            entry.get("city") or "意大利",
            entry.get("school") or urlparse(url).netloc,
            url,
        ))
    return out


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")
    entries = CONSERVATORIES + load_extra()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        items = list(pool.map(scrape_entry, entries))
    for item in items:
        item["checked_at"] = checked_at
        print(
            f"[{item['number']:02d}] {item['status']} {item['http_status']} "
            f"{item['city']} — deadlines={len(item['deadline_lines'])} dates={len(item['exam_dates'])} "
            f"req={len(item['requirements'])} pdf={len(item['documents'])}",
            flush=True,
        )
    OUT_PATH.write_text(
        json.dumps({"generated_at": checked_at, "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    readable = sum(1 for item in items if item["status"] == "ok")
    print(f"Saved {OUT_PATH} ({readable}/{len(items)} readable)")


if __name__ == "__main__":
    main()
