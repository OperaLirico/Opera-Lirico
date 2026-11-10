#!/usr/bin/env python3
"""Build a verified weekly Opera Lirico email digest.

The default mode only writes local HTML/text previews. With BUTTONDOWN_API_KEY set,
it may create a private draft; it never sends or publishes an email.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
ROME = ZoneInfo("Europe/Rome")
API_ROOT = "https://api.buttondown.com/v1"


def load_items(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    items = payload.get("items", [])
    return items if isinstance(items, list) else []


def parse_deadline(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def eligible_items(items: list[dict], now: dt.datetime) -> list[dict]:
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    selected = []
    for item in items:
        if item.get("publisher_status") != "official":
            continue
        if item.get("review_status") != "verified":
            continue
        if item.get("publication_status") != "published":
            continue
        deadline = parse_deadline(item.get("application_deadline_at"))
        if deadline is None or deadline <= now:
            continue
        if not item.get("title") or not item.get("announcement_url"):
            continue
        selected.append((deadline, item))
    selected.sort(key=lambda pair: pair[0])
    return [item for _, item in selected]


def _date_label(value: str) -> str:
    parsed = parse_deadline(value)
    if not parsed:
        return "截止日期待核实"
    return parsed.astimezone(ROME).strftime("%Y年%m月%d日 %H:%M（意大利时间）")


def build_digest(items: list[dict], now: dt.datetime) -> tuple[str, str, str]:
    valid = eligible_items(items, now)
    cutoff = now + dt.timedelta(days=14)
    urgent = [x for x in valid if parse_deadline(x["application_deadline_at"]) <= cutoff]
    later = [x for x in valid if x not in urgent]
    week = now.astimezone(ROME).strftime("%Y-%m-%d")
    slug = f"opera-lirico-weekly-{week}"

    def render_card(item: dict) -> str:
        title = html.escape(str(item.get("title", "")))
        source = html.escape(str(item.get("source_name", "官方来源")))
        location = html.escape(str(item.get("location", "地点以官方公告为准")))
        voices = "、".join(map(str, item.get("voice_types", []))) or "未注明"
        voices = html.escape(voices)
        summary = html.escape(str(item.get("eligibility_summary", "请查看官方公告确认资格。")))
        url = html.escape(str(item["announcement_url"]), quote=True)
        deadline = html.escape(_date_label(item.get("application_deadline_at")))
        return (
            '<article><h3><a href="' + url + '">' + title + '</a></h3>'
            '<p><strong>主办方：</strong>' + source + '　<strong>地点：</strong>' + location + '</p>'
            '<p><strong>声部：</strong>' + voices + '　<strong>报名截止：</strong>' + deadline + '</p>'
            '<p>' + summary + '</p><p><a href="' + url + '">查看官方公告</a></p></article>'
        )

    def section(title: str, records: list[dict]) -> str:
        if not records:
            return "<h2>" + title + "</h2><p>本期暂无符合条件的信息。</p>"
        return "<h2>" + title + "</h2>" + "".join(render_card(x) for x in records)

    body = (
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
        '<title>Opera Lirico 每周声乐机会简报</title>'
        '<body style="font-family:Arial,sans-serif;line-height:1.65;max-width:720px;margin:auto;padding:24px">'
        '<h1>Opera Lirico｜每周声乐机会简报</h1>'
        '<p>整理日期：' + html.escape(week) + '。仅收录已核验的官方发布信息；申请前请再次阅读主办方公告。</p>'
        + section("未来 14 天内截止", urgent)
        + section("其他仍开放的机会", later)
        + '<hr><p style="color:#666;font-size:12px">本简报根据本站已核验记录生成，不构成资格或报名结果保证。请以主办方最新公告为准。</p>'
        + '</body></html>'
    )
    lines = ["Opera Lirico｜每周声乐机会简报", f"整理日期：{week}", "",
             "仅收录已核验的官方发布信息；申请前请再次阅读主办方公告。", ""]
    for heading, records in (("未来 14 天内截止", urgent), ("其他仍开放的机会", later)):
        lines.extend([heading, ""])
        if not records:
            lines.append("本期暂无符合条件的信息。")
        for item in records:
            lines.extend([
                f"- {item.get('title', '')}",
                f"  主办方：{item.get('source_name', '官方来源')}；地点：{item.get('location', '以官方公告为准')}",
                f"  声部：{'、'.join(item.get('voice_types', [])) or '未注明'}",
                f"  截止：{_date_label(item.get('application_deadline_at'))}",
                f"  资格摘要：{item.get('eligibility_summary', '请查看官方公告确认资格。')}",
                f"  官方链接：{item.get('announcement_url', '')}", ""
            ])
    return slug, body, "\n".join(lines)


def _api_request(method: str, url: str, api_key: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": f"Token {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def create_private_draft(slug: str, subject: str, body: str, api_key: str) -> str:
    url = API_ROOT + "/emails/?status=draft"
    while url:
        page = _api_request("GET", url, api_key)
        for email in page.get("results", []):
            if email.get("slug") == slug:
                return "Draft already exists; skipped duplicate creation."
        url = page.get("next")
    _api_request("POST", API_ROOT + "/emails", api_key, {
        "subject": subject,
        "body": body,
        "status": "draft",
        "email_type": "private",
        "archival_mode": "disabled",
        "slug": slug,
    })
    return "Private draft created. No email was sent."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--now", help="ISO timestamp for deterministic tests")
    args = parser.parse_args()
    now = dt.datetime.fromisoformat(args.now) if args.now else dt.datetime.now(ROME)
    if now.tzinfo is None:
        parser.error("--now must include a timezone")
    opportunities = load_items(args.root / "data" / "opportunities.json")
    # Conservatory snapshots are loaded for integrity/context only. Their page-scrape
    # status is not equivalent to a verified, currently open application opportunity.
    schools = load_items(args.root / "data" / "conservatori.json")
    slug, body, plain = build_digest(opportunities, now)
    output = args.root / "build" / "email-draft"
    output.mkdir(parents=True, exist_ok=True)
    (output / "preview.html").write_text(body, encoding="utf-8")
    (output / "preview.txt").write_text(plain, encoding="utf-8")
    print(f"Draft-only preview generated: {len(eligible_items(opportunities, now))} verified open opportunities.")
    print(f"Conservatory snapshot loaded for context: {len(schools)} records.")
    print(f"Slug: {slug}")
    key = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    if key:
        try:
            print(create_private_draft(slug, f"Opera Lirico 每周简报｜{now.astimezone(ROME):%Y-%m-%d}", body, key))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            print(f"Draft API failed; preview retained. No send action was attempted: {exc}", file=sys.stderr)
            return 1
    else:
        print("BUTTONDOWN_API_KEY not configured; no remote draft created and nothing sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
