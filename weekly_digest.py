#!/usr/bin/env python3
"""Build a verified weekly Opera Lirico email digest.

Default mode writes local HTML/text previews. With BUTTONDOWN_API_KEY set, it may
create one private draft; it never sends or publishes an email.

The default (segmented) mode produces a single email whose body contains one
voice-specific block per voice part, guarded by
``{% if subscriber.metadata.voice == "..." %}``. Buttondown evaluates that per
subscriber at send time, so one draft serves every voice part without needing
paid tags or audience filters.
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
SITE_URL = "https://operalirico.github.io/Opera-Lirico/"
ARCHIVE_URL = "https://buttondown.com/wl19971007/archive"

VOICE_ORDER = (
    "soprano",
    "mezzo_soprano",
    "contralto",
    "countertenor",
    "tenor",
    "baritone",
    "bass",
)
VOICE_LABELS = {
    "soprano": "女高音",
    "mezzo_soprano": "女中音",
    "contralto": "女低音",
    "countertenor": "假声男高音",
    "tenor": "男高音",
    "baritone": "男中音",
    "bass": "男低音",
    "all_voices": "不限声部",
    "unspecified": "声部未注明",
}
# Reading guidance, not marketing copy: each line tells the reader what to check
# in the announcement before spending time on an application.
VOICE_GUIDE = {
    "soprano": "女高音的公告常在抒情与花腔之间分流。先看公告是否指定了角色或音域，再看截止日期，比先准备曲目更省时间。",
    "mezzo_soprano": "女中音的岗位数量通常少于女高音，但角色生命周期更长。遇到只写了剧目、没写角色的公告，去附件里确认具体角色。",
    "contralto": "女低音的岗位不多，而且部分意大利公告会把 contralto 与 mezzo 写在同一行。读的时候先确认它要的是哪一种，再决定是否申请。",
    "countertenor": "假声男高音的招募多来自巴洛克剧目与古乐团。公告里若同时出现 countertenor、alto、contratenor，通常指同一类声部。",
    "tenor": "男高音的试唱多要求一首意大利语咏叹调。公告写了角色名时，先对照角色音域与你目前稳定的舒适区，别只看剧目分量。",
    "baritone": "男中音的招募常常一次列出多个角色。读这类公告，先看哪几个角色由同一次试唱覆盖，再决定准备哪一段。",
    "bass": "男低音要区分 basso profondo 与 basso cantante，两者对音域和角色的要求不同。公告写清类型时，按类型准备。",
    "all_voices": "你没有指定声部，所以下面把本周所有声部的机会都列出来，并按截止时间排序。",
}


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


def item_voices(item: dict) -> set[str]:
    raw = item.get("voice_types") or []
    voices = {str(value) for value in raw if str(value).strip()}
    return voices or {"unspecified"}


def items_for_voice(items: list[dict], now: dt.datetime, voice: str) -> list[dict]:
    """Return verified open items whose announcement covers the given voice."""
    valid = eligible_items(items, now)
    if voice in ("all_voices", "", None):
        return valid
    wanted = voice
    selected = []
    for item in valid:
        voices = item_voices(item)
        if wanted in voices or "all_voices" in voices:
            selected.append(item)
    return selected


def _date_label(value: str) -> str:
    parsed = parse_deadline(value)
    if not parsed:
        return "截止日期待核实"
    return parsed.astimezone(ROME).strftime("%Y年%m月%d日 %H:%M（意大利时间）")


def _voice_label(value: str) -> str:
    if value in VOICE_LABELS:
        return VOICE_LABELS[value]
    return value


def _voices_text(item: dict) -> str:
    return "、".join(_voice_label(v) for v in sorted(item_voices(item))) or "未注明"


def render_card(item: dict) -> str:
    title = html.escape(str(item.get("title", "")))
    source = html.escape(str(item.get("source_name", "官方来源")))
    location = html.escape(str(item.get("location", "地点以官方公告为准")))
    voices = html.escape(_voices_text(item))
    summary = html.escape(str(item.get("eligibility_summary", "请查看官方公告确认资格。")))
    url = html.escape(str(item["announcement_url"]), quote=True)
    deadline = html.escape(_date_label(item.get("application_deadline_at")))
    return (
        '<article><h3><a href="' + url + '">' + title + '</a></h3>'
        '<p><strong>主办方：</strong>' + source + '　<strong>地点：</strong>' + location + '</p>'
        '<p><strong>声部：</strong>' + voices + '　<strong>报名截止：</strong>' + deadline + '</p>'
        '<p>' + summary + '</p><p><a href="' + url + '">查看官方公告</a></p></article>'
    )


def render_plain_card(item: dict) -> list[str]:
    return [
        f"- {item.get('title', '')}",
        f"  主办方：{item.get('source_name', '官方来源')}；地点：{item.get('location', '以官方公告为准')}",
        f"  声部：{_voices_text(item)}",
        f"  截止：{_date_label(item.get('application_deadline_at'))}",
        f"  资格摘要：{item.get('eligibility_summary', '请查看官方公告确认资格。')}",
        f"  官方链接：{item.get('announcement_url', '')}",
        "",
    ]


def _empty_note(label: str) -> str:
    return (
        "<p>本周没有新增点名" + html.escape(label) + "的已核验机会。"
        "上面的一般机会如果你也符合条件，可以一并看。</p>"
    )


def build_digest(items: list[dict], now: dt.datetime) -> tuple[str, str, str]:
    valid = eligible_items(items, now)
    cutoff = now + dt.timedelta(days=14)
    urgent = [x for x in valid if parse_deadline(x["application_deadline_at"]) <= cutoff]
    later = [x for x in valid if x not in urgent]
    week = now.astimezone(ROME).strftime("%Y-%m-%d")
    slug = f"opera-lirico-weekly-{week}"

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
            lines.extend(render_plain_card(item))
    return slug, body, "\n".join(lines)


def build_voice_block(items: list[dict], now: dt.datetime, voice: str) -> str:
    """HTML for one voice, to be wrapped in a per-subscriber conditional."""
    label = _voice_label(voice)
    records = items_for_voice(items, now, voice)[:5]
    guide = VOICE_GUIDE.get(voice, "")
    head = (
        '<h2 style="margin-top:26px">你的声部：' + html.escape(label) + "</h2>"
        + ('<p style="color:#555">' + html.escape(guide) + "</p>" if guide else "")
    )
    if not records:
        return head + _empty_note(label)
    return head + "".join(render_card(x) for x in records)


# Conditions for readers who never told us a voice (legacy subscribers, people
# who picked "声部未注明", and anyone whose metadata did not survive the write).
# They get the full list in deadline order instead of an empty personalised
# section. Buttondown's Django engine renders these last, so a named voice wins.
VOICE_FALLBACK_GUARDS = (
    "not subscriber.metadata.voice",
    'subscriber.metadata.voice == "unspecified"',
)


def build_fallback_block(items: list[dict], now: dt.datetime) -> str:
    """Whole-list section for subscribers without a usable voice value."""
    records = items_for_voice(items, now, "all_voices")[:5]
    head = (
        '<h2 style="margin-top:26px">还没填声部？这是本周全部机会</h2>'
        '<p style="color:#555">按报名截止时间排序。订阅时填一声部，'
        "就能在这一段换成只属于你的那几条。改声部回复任意一期邮件即可。</p>"
    )
    if not records:
        return head + "<p>本周暂无可展示的机会。</p>"
    return head + "".join(render_card(x) for x in records)


def build_personalized_digest(items: list[dict], now: dt.datetime) -> tuple[str, str, str]:
    """One email body that renders a voice-specific section per subscriber."""
    valid = eligible_items(items, now)
    week = now.astimezone(ROME).strftime("%Y-%m-%d")
    slug = f"opera-lirico-weekly-{week}-voiced"
    soon_cutoff = now + dt.timedelta(days=7)
    soon = [x for x in valid if parse_deadline(x["application_deadline_at"]) <= soon_cutoff][:3]
    listing = valid[:10]

    parts = [
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8">',
        '<title>Opera Lirico 每周声乐机会简报</title>',
        '<body style="font-family:Arial,sans-serif;line-height:1.65;max-width:720px;margin:auto;padding:24px">',
        "<h1>Opera Lirico｜每周声乐机会简报</h1>",
        '<p>整理日期：' + html.escape(week) + "。本期收录 " + str(len(valid))
        + " 条已核验且仍在报名的官方公告。申请前请再读一遍主办方原文，日期与资格以公告为准。</p>",
    ]

    # Per-voice sections. Each block is evaluated by Buttondown against the
    # subscriber's metadata.voice at send time.
    for voice in VOICE_ORDER:
        parts.append('{% if subscriber.metadata.voice == "' + voice + '" %}')
        parts.append(build_voice_block(items, now, voice))
        parts.append("{% endif %}")
    parts.append('{% if subscriber.metadata.voice == "all_voices" %}')
    parts.append(build_voice_block(items, now, "all_voices"))
    parts.append("{% endif %}")
    for guard in VOICE_FALLBACK_GUARDS:
        parts.append("{% if " + guard + " %}")
        parts.append(build_fallback_block(items, now))
        parts.append("{% endif %}")

    parts.append('<h2 style="margin-top:26px">一周内截止</h2>')
    if soon:
        parts.extend(render_card(x) for x in soon)
    else:
        parts.append("<p>未来七天没有即将截止的公告。</p>")

    parts.append('<h2 style="margin-top:26px">全部开放机会</h2>')
    if listing:
        parts.append('<ol style="padding-left:20px">')
        for item in listing:
            url = html.escape(str(item["announcement_url"]), quote=True)
            parts.append(
                '<li><a href="' + url + '">' + html.escape(str(item.get("title", ""))) + "</a>　"
                + html.escape(_voices_text(item)) + "　截止 "
                + html.escape(_date_label(item.get("application_deadline_at"))) + "</li>"
            )
        parts.append("</ol>")
    else:
        parts.append("<p>本期暂无符合条件的公告。</p>")

    parts.extend([
        '<hr style="margin-top:26px">',
        '<p style="color:#666;font-size:12px">本简报由 OperaLab. 根据本站已核验记录生成，'
        "不构成资格或报名结果保证。</p>",
        '<p style="color:#666;font-size:12px">声部信息只用于决定你收到内容，不对外展示。'
        '想改声部，回复这封邮件说明即可。<br>'
        '退订：邮件页脚的退订链接随时可用。<br>'
        '隐私说明：<a href="' + SITE_URL + 'privacy.html">' + SITE_URL + "privacy.html</a><br>"
        '往期：<a href="' + ARCHIVE_URL + '">' + ARCHIVE_URL + "</a></p>",
        "</body></html>",
    ])
    body = "".join(parts)

    lines = [
        "Opera Lirico｜每周声乐机会简报",
        f"整理日期：{week}",
        "",
        f"本期收录 {len(valid)} 条已核验且仍在报名的官方公告。",
        "",
    ]
    for voice in VOICE_ORDER + ("all_voices",):
        lines.extend([f"【{_voice_label(voice)}】", VOICE_GUIDE.get(voice, "")])
        records = items_for_voice(items, now, voice)[:5]
        if not records:
            lines.append("本周没有新增点名该声部的已核验机会。")
        for item in records:
            lines.extend(render_plain_card(item))
    lines.extend(["还没填声部／声部未注明：本周全部机会", ""])
    for item in items_for_voice(items, now, "all_voices")[:5]:
        lines.extend(render_plain_card(item))
    lines.extend(["一周内截止", ""])
    if soon:
        for item in soon:
            lines.extend(render_plain_card(item))
    else:
        lines.append("未来七天没有即将截止的公告。")
    lines.extend(["全部开放机会", ""])
    for item in listing:
        lines.append(f"- {item.get('title', '')}（{_voices_text(item)}）")
    return slug, body, "\n".join(lines)


def _api_request(method: str, url: str, api_key: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": f"Token {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Include the HTTP method, endpoint path, and safe response body for diagnosis.
        # Never include request headers, which contain the API key.
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        path = urllib.parse.urlsplit(url).path
        raise RuntimeError(
            f"Buttondown {method} {path} returned HTTP {exc.code}: {detail}"
        ) from exc


def create_private_draft(slug: str, subject: str, body: str, api_key: str) -> str:
    url = API_ROOT + "/emails?status=draft"
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


def subject_line(now: dt.datetime) -> str:
    week = now.astimezone(ROME)
    return f"Opera Lirico 每周简报｜{week:%Y-%m-%d}｜按你的声部"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--now", help="ISO timestamp for deterministic tests")
    parser.add_argument(
        "--mode", choices=("segmented", "single"), default="segmented",
        help="segmented: one draft with per-voice conditional sections; single: one flat digest",
    )
    args = parser.parse_args()
    now = dt.datetime.fromisoformat(args.now) if args.now else dt.datetime.now(ROME)
    if now.tzinfo is None:
        parser.error("--now must include a timezone")
    opportunities = load_items(args.root / "data" / "opportunities.json")
    # Conservatory snapshots are loaded for integrity/context only. Their page-scrape
    # status is not equivalent to a verified, currently open application opportunity.
    schools = load_items(args.root / "data" / "conservatori.json")
    if args.mode == "segmented":
        slug, body, plain = build_personalized_digest(opportunities, now)
    else:
        slug, body, plain = build_digest(opportunities, now)

    output = args.root / "build" / "email-draft"
    output.mkdir(parents=True, exist_ok=True)
    (output / "preview.html").write_text(body, encoding="utf-8")
    (output / "preview.txt").write_text(plain, encoding="utf-8")
    if args.mode == "segmented":
        for voice in VOICE_ORDER + ("all_voices",):
            rendered = (
                '<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
                '<body style="font-family:Arial,sans-serif;line-height:1.65;max-width:720px;'
                'margin:auto;padding:24px">'
                + build_voice_block(opportunities, now, voice)
                + "</body></html>"
            )
            (output / f"voice-{voice}.html").write_text(rendered, encoding="utf-8")
    print(f"Digest mode: {args.mode}. Verified open opportunities: {len(eligible_items(opportunities, now))}.")
    print(f"Conservatory snapshot loaded for context: {len(schools)} records.")
    print(f"Slug: {slug}")
    key = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    if key:
        try:
            print(create_private_draft(slug, subject_line(now) if args.mode == "segmented"
                                        else f"Opera Lirico 每周简报｜{now.astimezone(ROME):%Y-%m-%d}",
                                        body, key))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, RuntimeError) as exc:
            print(f"Draft API failed; preview retained. No send action was attempted: {exc}", file=sys.stderr)
            return 1
    else:
        print("BUTTONDOWN_API_KEY not configured; no remote draft created and nothing sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
