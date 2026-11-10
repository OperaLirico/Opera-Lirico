#!/usr/bin/env python3
"""Fetch public Italian vocal-opportunity pages with Scrapling."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scrapling.fetchers import Fetcher

from robots_policy import fetch_page_with_robots


SOURCES = [
    (1, "Teatro alla Scala", "https://www.teatroallascala.org/it/il-teatro/lavora-con-noi/concorsi-e-audizioni-coro.html"),
    (2, "Teatro Carlo Felice", "https://carlofelice.it/audizioni-e-concorsi/"),
    (3, "Teatro Massimo", "https://www.teatromassimo.it/audizioni/"),
    (4, "Teatro Regio Torino", "https://www.teatroregio.torino.it/selezione-personale"),
    (5, "Teatro dell'Opera di Roma - Fabbrica", "https://www.operaroma.it/bandi-e-concorsi/bandi-fabbrica-young-artist-program-2027-2028/"),
    (6, "Teatro Verdi Trieste", "https://www.teatroverdi-trieste.com/amministrazione-tras/bandi-di-concorso-2026/"),
    (7, "Teatro Comunale di Bologna", "https://www.tcbo.it/amministrazione-trasparente/"),
    (8, "Maggio Musicale Fiorentino", "https://www.maggiofiorentino.com/bandi/"),
    (9, "AsLiCo", "https://aslico.org/edizione-in-corso/"),
    (10, "Teatro Lirico Sperimentale di Spoleto", "https://www.tls-belli.it/bandi_e_avvisi/"),
    (11, "Fondazione Luciano Pavarotti", "https://www.lucianopavarottifoundation.com/c/news/"),
    (12, "Ente Lirico Italiano - Premio E.L.I.", "https://www.enteliricoitaliano.it/premioeli/bando-concorso-2026/"),
    (13, "Tommaso Traetta Opera Festival", "https://www.traettafestival.it/sito/tof/concorsi/concorso-internazionale-di-canto-lirico-tommaso-traetta/"),
    (14, "CLIP Portofino", "https://www.portofinoclip.it/clip-2026/"),
    (15, "Concorso Francesco Morlacchi", "https://www.concorsomorlacchi.it/"),
    (16, "Teatro La Fenice - 招募与选拔", "https://www.teatrolafenice.it/fondazione-teatro-la-fenice/lavora-con-noi/"),
    (17, "Teatro Lirico di Cagliari - 招募与选拔", "https://www.liricocagliari.it/trasparenza/"),
    (18, "Accademia d'Arte Lirica di Osimo", "https://www.accademialiricaosimo.com/"),
    (19, "Sipario Lirico APS - 试唱", "https://www.siparioliricoaps.it/audizioni/"),
    (20, "Valsesia Musica - 声乐比赛", "https://www.valsesiamusica.com/sezione_canto_lirico.htm"),
    (21, "Premio Fausto Ricci - 国际声乐比赛", "https://www.xxisecolo.org/faustoricci/opera.html"),
    (22, "Concorso Maria Malibran - 国际声乐比赛", "https://www.mariamalibran.it/xi-edizione-2026.html"),
    (23, "Agnesi Opera Competition", "https://www.agnesioperacompetition.com/"),
    (24, "Nicola Martinucci 国际歌剧比赛", "https://nicolamartinucciprize.com/"),
    (25, "Norma Fantini Opera Contest", "https://www.normafantinioperacontest.it/"),
    (26, "Renata Tebaldi 国际声乐比赛", "https://www.fondazionerenatatebaldi.org/"),
    (27, "Sportello Spettacolo（演艺行业信息平台）", "https://www.sportellospettacolo.it/bandi-call/"),
    (28, "Opera Mundus（歌剧比赛信息平台）", "https://www.operamundus.com/en/concorsi/"),
    (29, "Liricamente（声乐行业信息平台）", "https://www.liricamente.it/audizioni-canto-lirico-cori-cantanti-lirici.asp"),
]

KEYWORDS = re.compile(
    r"audizion|concor|bando|iscrizion|scadenz|candidat|cantant|coro|soprano|"
    r"mezzosoprano|contralto|tenore|baritono|basso|giovani voci|young artist|"
    r"2026|2027|chius[oa]|apert[oa]",
    re.IGNORECASE,
)
DEADLINE_RE = re.compile(r"scadenz|entro|termine|iscrizion|apert[oa]|chius[oa]|deadlin|application", re.IGNORECASE)
ANNOUNCEMENT_RE = re.compile(r"audizion|concor|bando|selezion|candidat|casting", re.IGNORECASE)
DATE_RE = re.compile(r"\b(?:\d{1,2}[./-]\d{1,2}[./-]20\d{2}|\d{1,2}\s+[a-zà-ÿ]+\s+20\d{2}|20\d{2})\b", re.IGNORECASE)
GENERIC_LINES = {"coro", "concorso", "audizioni", "audizione", "bando", "news", "home", "privacy", "cookie"}


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def fetch_public_page(url: str, timeout: int = 30):
    """Fetch a public page only after robots checks for every redirect hop."""
    return fetch_page_with_robots(
        url, Fetcher.get, timeout=timeout, retries=0, delay=0
    )


def rank_relevant_lines(lines: list[str]) -> list[str]:
    ranked: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        if not KEYWORDS.search(line) or line.casefold() in GENERIC_LINES:
            continue
        if len(line) < 22 and not DATE_RE.search(line):
            continue
        score = 0
        if DEADLINE_RE.search(line):
            score += 5
        if ANNOUNCEMENT_RE.search(line):
            score += 3
        if DATE_RE.search(line):
            score += 2
        if re.search(r"soprano|mezzosoprano|contralto|tenore|baritono|basso|ruolo|young artist", line, re.IGNORECASE):
            score += 1
        ranked.append((-score, index, line))
    return [line for _, _, line in sorted(ranked)[:15]]


def preserve_last_good(previous: dict | None, current: dict, attempted_at: str) -> dict:
    """Keep the last successful extract when a refresh fails.

    status describes the stored snapshot; last_attempt_status describes the
    latest network attempt. Transient failures therefore cannot erase data.
    """
    if current.get("status") == "ok":
        current["checked_at"] = attempted_at
        current["last_success_at"] = attempted_at
        current["last_attempt_at"] = attempted_at
        current["last_attempt_status"] = "ok"
        current["last_attempt_http_status"] = current.get("http_status")
        current["last_attempt_error"] = None
        current["last_attempt_access_policy"] = current.get("access_policy")
        current["consecutive_failures"] = 0
        current["stale"] = False
        return current

    if previous and previous.get("status") == "ok":
        kept = dict(previous)
        kept.update({
            "number": current.get("number", previous.get("number")),
            "source": current.get("source", previous.get("source")),
            "url": current.get("url", previous.get("url")),
            "last_attempt_at": attempted_at,
            "last_attempt_status": current.get("status", "error"),
            "last_attempt_http_status": current.get("http_status"),
            "last_attempt_error": current.get("error"),
            "last_attempt_access_policy": current.get("access_policy"),
            "consecutive_failures": int(previous.get("consecutive_failures", 0)) + 1,
            "stale": True,
        })
        return kept

    current["checked_at"] = attempted_at
    current["last_attempt_at"] = attempted_at
    current["last_attempt_status"] = current.get("status", "error")
    current["last_attempt_http_status"] = current.get("http_status")
    current["last_attempt_error"] = current.get("error")
    current["last_attempt_access_policy"] = current.get("access_policy")
    current["consecutive_failures"] = int((previous or {}).get("consecutive_failures", 0)) + 1
    current["stale"] = True
    return current


def main() -> None:
    out_dir = Path(__file__).resolve().parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")
    previous_path = out_dir / "sources.json"
    try:
        previous_items = json.loads(previous_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        previous_items = []
    previous_by_number = {item.get("number"): item for item in previous_items}
    results: list[dict] = []

    for number, name, url in SOURCES:
        item = {
            "number": number,
            "source": name,
            "url": url,
            "checked_at": checked_at,
            "status": "error",
            "http_status": None,
            "title": "",
            "page_text": "",
            "relevant_lines": [],
            "error": None,
            "access_policy": None,
        }
        try:
            response, access = fetch_public_page(url, timeout=30)
            item["access_policy"] = access
            if response is None:
                item["status"] = access.get("status", "robots_policy_unavailable")
                item["http_status"] = access.get("http_status")
                item["error"] = access.get("reason") or access.get("robots_url") or item["status"]
            else:
                item["http_status"] = getattr(response, "status", None)
                item["status"] = "ok" if item["http_status"] and item["http_status"] < 400 else "http_error"
                item["title"] = clean_line(response.css("title::text").get() or "")
                text = response.get_all_text(separator="\n") or ""
                lines = [clean_line(line) for line in text.splitlines()]
                lines = [line for line in lines if line]
                item["relevant_lines"] = rank_relevant_lines(lines)
                if not item["title"] and not lines:
                    item["status"] = "extraction_error"
                    item["error"] = "The page returned no readable title or text."
        except Exception as exc:  # Keep going so one inaccessible site does not stop the batch.
            item["error"] = f"{type(exc).__name__}: {exc}"
        item = preserve_last_good(previous_by_number.get(number), item, checked_at)
        results.append(item)
        print(
            f"[{number:02d}/{len(SOURCES):02d}] snapshot={item['status']} "
            f"attempt={item.get('last_attempt_status', item['status'])} "
            f"http={item.get('last_attempt_http_status', item['http_status'])} "
            f"stale={item.get('stale', False)} {name} — {item['title'][:100]}",
            flush=True,
        )
        time.sleep(1.2)

    json_path = out_dir / "sources.json"
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path = out_dir / "scrapling_report.md"
    with report_path.open("w", encoding="utf-8") as report:
        report.write("# Scrapling 首轮抓取结果\n\n")
        report.write(f"抓取时间：{checked_at}（Europe/Rome）\n\n")
        report.write("本文件记录 Scrapling 直接访问公开来源页后的结果。页面可访问不代表公告仍有效；报名状态需依据公告日期和截止时间人工判读。\n\n")
        for item in results:
            report.write(f"## {item['number']}. {item['source']}\n\n")
            report.write(f"- 页面：[{item['url']}]({item['url']})\n")
            report.write(
                f"- 快照状态：{item['status']}；HTTP：{item['http_status']}；"
                f"是否沿用旧快照：{'是' if item.get('stale') else '否'}\n"
            )
            if item.get("last_attempt_status") and item.get("stale"):
                report.write(
                    f"- 最近一次尝试：{item.get('last_attempt_status')}；"
                    f"时间：{item.get('last_attempt_at', '未知')}；"
                    f"连续失败：{item.get('consecutive_failures', 0)} 次\n"
                )
            report.write(f"- 页面标题：{item['title'] or '未读取到'}\n")
            if item["error"]:
                report.write(f"- 错误：`{item['error']}`\n")
            if item["relevant_lines"]:
                report.write("- 公告相关原文片段：\n")
                for line in item["relevant_lines"][:35]:
                    report.write(f"  - {line}\n")
            else:
                report.write("- 未筛出匹配公告关键词的文字；可能是页面结构、脚本渲染或访问限制导致。\n")
            report.write("\n")
    print(f"Saved {json_path}")
    print(f"Saved {report_path}")


if __name__ == "__main__":
    main()
