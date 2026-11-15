#!/usr/bin/env python3
"""Rule-based first-pass review for the private content queue (L4 automation).

The review queue is human-first by design. This script adds a narrow, auditable
automation layer in front of it:

* every pending draft is re-checked against machine-verifiable rules
* only drafts that pass *all* rules are approved automatically
* everything else stays ``pending_review`` and is annotated so a human still
  sees it, together with the reason the machine refused to decide
* nothing is ever published to a social network: publishing stays manual

The rules are deliberately conservative. A wrong "pending_review" costs one
click; a wrong "approved" puts an unverified claim in front of readers.
"""
from __future__ import annotations

import http.cookiejar
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("OPS_DASHBOARD_URL", "https://opera-lirico-ops.wl19971007.workers.dev").rstrip("/")
PASSWORD = os.environ.get("OPS_DASHBOARD_PASSWORD", "")
MAX_APPROVALS = int(os.environ.get("AUTO_REVIEW_MAX_APPROVALS", "8"))
MIN_AGE_MINUTES = int(os.environ.get("AUTO_REVIEW_MIN_AGE_MINUTES", "60"))
REVIEWER = "auto-review-v1"

BANNED_CLAIMS = re.compile(
    r"保证|100%|全网最低|最低价|第一品牌|绝对(?:可靠|有效)|国家级|权威认证|包过|速抢|最后机会|稳赚"
)
SHORTENER_HOSTS = {"bit.ly", "t.co", "tinyurl.com", "goo.gl", "ow.ly", "is.gd", "buff.ly", "linktr.ee"}


def request(opener, path, payload=None, method=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    verb = method or ("GET" if payload is None else "POST")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=verb,
        headers={
            "Accept": "application/json",
            "Origin": BASE,
            "User-Agent": "OperaLiricoAutoReview/1.0",
            **({"Content-Type": "application/json"} if data else {}),
        },
    )
    try:
        with opener.open(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read(1024).decode("utf-8", errors="replace")
        raise RuntimeError(f"dashboard request failed: HTTP {exc.code}; {detail[:300]}") from None


def official_hosts() -> set[str]:
    """Hosts the project already treats as official sources."""
    hosts: set[str] = set()
    for name in ("sources.json", "masterclass_sources.json", "opportunities.json", "masterclasses.json"):
        path = ROOT / "data" / name
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        items = payload.get("items") if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            for key in ("source_url", "url", "official_source_url", "official_evidence_url"):
                value = item.get(key)
                if isinstance(value, str) and value.startswith("https://"):
                    host = urlparse(value).hostname
                    if host:
                        hosts.add(host.lower())
    return hosts


def host_matches(host: str, allowed: set[str]) -> bool:
    """True when host is an allowed domain or a subdomain of one."""
    return any(host == candidate or host.endswith("." + candidate) for candidate in allowed)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def judge(draft: dict, allowed_hosts: set[str], approved_captions: set[str]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    title = str(draft.get("title") or "").strip()
    caption = str(draft.get("caption") or "").strip()
    source_url = str(draft.get("source_url") or "").strip()
    category = str(draft.get("category") or "").strip()

    if not title or len(title) > 120:
        reasons.append("标题缺失或超过 120 字")
    if not caption:
        reasons.append("正文为空")
    elif len(caption) < 120:
        reasons.append(f"正文过短（{len(caption)} 字），证据不足以自动通过")
    elif len(caption) > 900:
        reasons.append(f"正文过长（{len(caption)} 字），需要人工删减")

    parsed = urlparse(source_url) if source_url else None
    if not parsed or parsed.scheme != "https" or not parsed.hostname:
        reasons.append("来源链接缺失或不是 HTTPS")
    else:
        host = parsed.hostname.lower()
        if host in SHORTENER_HOSTS:
            reasons.append("来源是短链跳转，无法核实原文")
        elif allowed_hosts and not host_matches(host, allowed_hosts):
            reasons.append(f"来源域名不在官方来源清单内：{host}")

    hit = BANNED_CLAIMS.search(caption) or BANNED_CLAIMS.search(title)
    if hit:
        reasons.append(f"出现未经核实的绝对化表述：{hit.group(0)}")

    if not category:
        reasons.append("缺少内容分类")

    first_block = normalize(caption)[:120]
    if first_block and first_block in approved_captions:
        reasons.append("与已通过的内容重复")

    return (not reasons, reasons)


def main() -> int:
    if not PASSWORD or len(PASSWORD) < 32:
        print("OPS_DASHBOARD_PASSWORD 缺失或过短，跳过自动审核。", file=sys.stderr)
        return 1

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    request(opener, "/api/login", {"password": PASSWORD})

    drafts = request(opener, "/api/content/drafts").get("items") or []
    allowed_hosts = official_hosts()
    approved_captions = {
        normalize(str(item.get("caption") or ""))[:120]
        for item in drafts
        if item.get("status") in {"approved", "published"}
    }

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=MIN_AGE_MINUTES)
    approved = 0
    escalated = 0
    skipped = 0

    for draft in drafts:
        if draft.get("status") != "pending_review":
            continue
        draft_id = str(draft.get("id") or "")
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", draft_id):
            continue

        created_raw = str(draft.get("created_at") or "")
        try:
            created = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        except ValueError:
            created = None
        if created and created > cutoff:
            skipped += 1  # too fresh: the generator may still be writing this batch
            continue

        ok, reasons = judge(draft, allowed_hosts, approved_captions)
        if ok and approved >= MAX_APPROVALS:
            ok, reasons = False, [f"本轮自动通过已达上限 {MAX_APPROVALS} 条"]

        review = {
            "reviewer": REVIEWER,
            "auto": True,
            "decided_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "reasons": reasons[:6],
        }
        request(
            opener,
            f"/api/content/drafts/{draft_id}",
            {
                "status": "approved" if ok else "pending_review",
                "review": review,
            },
            method="PATCH",
        )
        if ok:
            approved += 1
            approved_captions.add(normalize(str(draft.get("caption") or ""))[:120])
            print(f"approved  {draft_id}  {str(draft.get('title') or '')[:60]}")
        else:
            escalated += 1
            print(f"escalated {draft_id}  {' / '.join(reasons[:3])}")

    print(
        f"\nsummary: approved={approved} escalated={escalated} "
        f"too_fresh={skipped} total_pending={sum(1 for d in drafts if d.get('status') == 'pending_review')}"
    )
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("## 自动审核\n")
            handle.write(f"- 自动通过：**{approved}**\n")
            handle.write(f"- 升级人工：**{escalated}**\n")
            handle.write(f"- 生成中跳过：**{skipped}**\n")
            handle.write(f"- 规则版本：`{REVIEWER}`\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
