#!/usr/bin/env python3
"""Generate private Chinese social drafts from verified, published records only."""
from __future__ import annotations
import html, json, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "social-drafts"
TODAY = datetime.now(ZoneInfo("Europe/Rome")).date()
VOICE = {"soprano":"女高音","mezzo_soprano":"次女高音","contralto":"女低音","countertenor":"假声男高音","tenor":"男高音","baritone":"男中音","bass":"男低音","all_voices":"所有声部","unspecified":"声部以官方公告为准"}

def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default

def date_is_current(value):
    if not value:
        return True
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.date() >= TODAY
    except (TypeError, ValueError):
        return False

def safe_id(value):
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value)).strip("-")[:80] or "item"

def card_svg(title, category, location, deadline, source, url):
    esc = lambda x: html.escape(str(x or ""), quote=True)
    # Character slicing keeps Chinese titles readable without relying on Latin word breaks.
    title_lines = [title[i:i+16] for i in range(0, min(len(title), 48), 16)] or ["音乐机会"]
    lines = "".join(f'<text x="72" y="{390+i*78}" font-family="Noto Sans CJK SC, sans-serif" font-size="54" font-weight="600" fill="#173d32">{esc(line)}</text>' for i, line in enumerate(title_lines[:3]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440" role="img" aria-label="{esc(title)}">
<rect width="1080" height="1440" fill="#f5f0e5"/><rect x="42" y="42" width="996" height="1356" rx="8" fill="none" stroke="#c9bda7" stroke-width="2"/>
<text x="72" y="130" font-family="Georgia,serif" font-size="30" letter-spacing="7" fill="#8b2635">OPERA LIRICO</text>
<path d="M72 190H1008" stroke="#173d32" stroke-width="3"/>
<text x="72" y="285" font-family="Arial,sans-serif" font-size="30" letter-spacing="4" fill="#8b2635">{esc(category)}</text>
{lines}
<path d="M72 650H1008" stroke="#c9bda7" stroke-width="2"/>
<text x="72" y="740" font-family="Arial,sans-serif" font-size="34" fill="#173d32">{esc(location or "地点以官方公告为准")}</text>
<text x="72" y="820" font-family="Arial,sans-serif" font-size="30" fill="#4c5c53">{esc(deadline or "申请时间请查看官方公告")}</text>
<text x="72" y="1210" font-family="Arial,sans-serif" font-size="24" fill="#66736c">官方来源：{esc(source)}</text>
<text x="72" y="1270" font-family="Arial,sans-serif" font-size="18" fill="#66736c">{esc(url[:76])}</text>
<text x="72" y="1350" font-family="Arial,sans-serif" font-size="22" letter-spacing="2" fill="#173d32">发现机会 · 核对官方公告 · 自主申请</text>
</svg>"""

def eligible(item, category):
    if not (item.get("publisher_status") == "official" and item.get("review_status") == "verified" and item.get("publication_status") == "published"):
        return False
    if not item.get("id") or not item.get("title") or not item.get("source_url") or not item.get("source_name"):
        return False
    if category == "声乐大师班":
        # A masterclass needs a dated upcoming session; undated listings are not promoted.
        date_value = item.get("application_deadline_at") or item.get("end_at") or item.get("start_at")
        return bool(date_value) and date_is_current(date_value)
    return date_is_current(item.get("application_deadline_at"))

def records():
    sources = [
        ("opportunity", ROOT / "data" / "opportunities.json"),
        ("masterclass", ROOT / "data" / "masterclasses.json"),
    ]
    labels = {"vocal_competition": "国际声乐比赛", "audition": "歌剧院招聘", "choir_audition": "合唱团招聘", "academy": "青年艺术家项目", "masterclass": "声乐大师班"}
    for kind, path in sources:
        data = load(path, {"items": []})
        for item in data.get("items", []):
            category = "声乐大师班" if kind == "masterclass" else labels.get(item.get("opportunity_type"), "音乐机会")
            if eligible(item, category):
                yield category, item

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index, used_ids = [], set()
    for category, item in records():
        ident = safe_id(item["id"])
        if ident in used_ids:
            ident = f"{ident}-{len(used_ids)+1}"
        used_ids.add(ident)
        title = str(item.get("title") or "音乐机会")
        location = item.get("location", "")
        deadline_raw = item.get("application_deadline_at") or ""
        try:
            deadline_dt = datetime.fromisoformat(str(deadline_raw).replace("Z", "+00:00"))
            deadline = deadline_dt.strftime("%Y-%m-%d %H:%M")
        except (TypeError, ValueError):
            deadline = str(deadline_raw)[:10]
        source = item.get("source_name", "")
        url = item.get("application_url") or item.get("source_url", "")
        voices = "、".join(VOICE.get(v, v) for v in item.get("voice_types", []) if v)
        facts = [f"类别：{category}", f"地点：{location or '以官方公告为准'}"]
        if item.get("teacher"): facts.append(f"导师：{item['teacher']}")
        if voices: facts.append(f"声部：{voices}")
        if deadline: facts.append(f"申请截止：{deadline}（意大利当地时间）")
        if item.get("fee_eur") is not None: facts.append(f"报名费用：€{item['fee_eur']}")
        if item.get("start_at"): facts.append(f"活动开始：{str(item['start_at'])[:10]}")
        if item.get("eligibility_summary"): facts.append(f"申请要求：{item['eligibility_summary']}")
        facts += [f"官方来源：{source}", f"官方链接：{url}", f"最近核验：{item.get('last_verified_at') or item.get('checked_at') or '未记录'}"]
        body = f"# {title}\n\n{category}｜Opera Lirico 精选\n\n这是一条面向声乐学习者与青年歌唱家的机会信息。建议先确认自身条件，再通过官方渠道提交申请。\n\n" + "\n".join(f"- {x}" for x in facts) + "\n\n**申请提醒**：具体资格、曲目、材料与预选安排，请以官方章程为准；信息可能更新，提交前请再次核对官方页面。\n\n更多欧洲声乐机会，关注 Italia Audizioni。\n\n#古典音乐 #声乐 #歌剧 #音乐留学 #国际声乐比赛"
        (OUT / f"{ident}.md").write_text(body, encoding="utf-8")
        card_deadline = ("报名截止：" + deadline) if deadline else "具体时间请查看官方公告"
        (OUT / f"{ident}.svg").write_text(card_svg(title, category, location, card_deadline, source, url), encoding="utf-8")
        cairosvg.svg2png(bytestring=(OUT / f"{ident}.svg").read_bytes(), write_to=str(OUT / f"{ident}.png"), output_width=1080, output_height=1440)
        index.append({"id": ident, "category": category, "title": title, "status": "draft", "markdown": f"{ident}.md", "image": f"{ident}.png", "source_svg": f"{ident}.svg", "source_url": url})
    (OUT / "index.json").write_text(json.dumps({"generated_at": datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds"), "count": len(index), "items": index}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(index)} private draft(s) from verified published records.")

if __name__ == "__main__":
    main()
