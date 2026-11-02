#!/usr/bin/env python3
"""Fetch the 15 public Italian vocal-opportunity source pages with Scrapling."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scrapling.fetchers import Fetcher


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
]

KEYWORDS = re.compile(
    r"audizion|concor|bando|iscrizion|scadenz|candidat|cantant|coro|soprano|"
    r"mezzosoprano|contralto|tenore|baritono|basso|giovani voci|young artist|"
    r"2026|2027|chius[oa]|apert[oa]",
    re.IGNORECASE,
)


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def main() -> None:
    out_dir = Path(__file__).resolve().parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds")
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
        }
        try:
            response = Fetcher.get(url, timeout=30, retries=0)
            item["http_status"] = getattr(response, "status", None)
            item["status"] = "ok" if item["http_status"] and item["http_status"] < 400 else "http_error"
            item["title"] = clean_line(response.css("title::text").get() or "")
            text = response.get_all_text(separator="\n") or ""
            lines = [clean_line(line) for line in text.splitlines()]
            lines = [line for line in lines if line]
            item["relevant_lines"] = [line for line in lines if KEYWORDS.search(line)][:15]
        except Exception as exc:  # Keep going so one inaccessible site does not stop the batch.
            item["error"] = f"{type(exc).__name__}: {exc}"
        results.append(item)
        print(f"[{number:02d}/15] {item['status']} {item['http_status']} {name} — {item['title'][:100]}", flush=True)
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
            report.write(f"- 抓取状态：{item['status']}；HTTP：{item['http_status']}\n")
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
