#!/usr/bin/env python3
"""Access-traffic watchdog: fails the run when analytics silently stops reporting.

The dashboard once showed "—" for a week because the GraphQL query used the
beacon token as ``siteTag``. Nothing alerted, because an empty result looked
exactly like "no visitors". This script exists so that condition can never
pass unnoticed again.

Exit code 0 = traffic data is present and consistent.
Exit code 1 = anomaly; the failure digest and self-heal workflow pick it up.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

GRAPHQL = "https://api.cloudflare.com/client/v4/graphql"
HEALTH = os.environ.get("OPS_HEALTH_URL", "https://opera-lirico-ops.wl19971007.workers.dev/api/health")
ACCOUNT = os.environ.get("CF_ACCOUNT_ID", "")
TOKEN = os.environ.get("CF_ANALYTICS_API_TOKEN", "")
# The GraphQL siteTag is the Web Analytics site id, not the beacon token.
SITE_TAG = os.environ.get("CF_WEB_ANALYTICS_SITE_TAG", "e6657aea01794d4295506abb40a09e99")

QUERY = (
    'query { viewer { accounts(filter: { accountTag: "%s" }) { '
    'rumPageloadEventsAdaptiveGroups(limit: 1000, filter: { siteTag: "%s", date_geq: "%s", date_leq: "%s" }) '
    "{ count sum { visits } dimensions { date } } } } }"
)


def post_json(url: str, payload: dict, headers: dict, timeout: int = 25) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "OperaLiricoWatchdog/1.0", **headers},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(url: str, timeout: int = 15) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "OperaLiricoWatchdog/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))



def assess_traffic_freshness(
    pageviews_7d: int,
    pageviews_last_48h: int,
    latest_date: date | None,
    today: date,
) -> tuple[list[str], list[str]]:
    """Avoid treating a quiet site or Cloudflare's reporting delay as an outage.

    Cloudflare documents up to 24 hours of analytics delay on Free plans.
    A zero in the rolling two-day bucket is therefore a warning while the
    latest observed day is within the last 72 hours; it becomes an error only
    when the data itself is older than that grace window.
    """
    problems: list[str] = []
    notes: list[str] = []

    if pageviews_7d >= 30 and pageviews_last_48h == 0:
        if latest_date and latest_date >= today - timedelta(days=2):
            notes.append(
                f"最近 48 小时没有浏览记录；最近一次统计为 {latest_date.isoformat()}，"
                "仍在 72 小时容忍窗口内，可能是低流量或统计延迟，暂不判定上报中断"
            )
        else:
            problems.append(
                "最近 48 小时浏览量为 0，且最近统计日期已超出 72 小时容忍窗口"
            )

    if pageviews_7d >= 10 and latest_date and latest_date < today - timedelta(days=2):
        problems.append(
            f"最新统计停留在 {latest_date.isoformat()}，已超过 72 小时没有新数据"
        )

    return problems, notes


def main() -> int:
    problems: list[str] = []
    notes: list[str] = []

    if not TOKEN or not ACCOUNT:
        print("CF_ANALYTICS_API_TOKEN 或 CF_ACCOUNT_ID 缺失，无法运行看门狗。", file=sys.stderr)
        return 1

    today = datetime.now(timezone.utc).date()
    start = (today - timedelta(days=6)).isoformat()
    end = today.isoformat()

    body = post_json(
        GRAPHQL,
        {"query": QUERY % (ACCOUNT, SITE_TAG, start, end)},
        {"Authorization": "Bearer " + TOKEN},
    )
    if body.get("errors"):
        problems.append("Cloudflare GraphQL 返回错误：" + str(body["errors"])[:300])

    accounts = ((body.get("data") or {}).get("viewer") or {}).get("accounts") or []
    rows = (accounts[0] if accounts else {}).get("rumPageloadEventsAdaptiveGroups") or []
    if not accounts:
        problems.append("账户查询返回空：CF_ACCOUNT_ID 与 Token 作用域不一致")
    elif not rows:
        problems.append(f"最近 7 天（{start} 至 {end}）没有任何统计记录：siteTag 可能失效或脚本未上报")

    days = []
    for row in rows:
        try:
            days.append(
                {
                    "date": date.fromisoformat(row["dimensions"]["date"]),
                    "pageviews": int(row["count"]),
                    "visits": int((row.get("sum") or {}).get("visits") or 0),
                }
            )
        except (KeyError, TypeError, ValueError):
            problems.append("返回结构异常：" + str(row)[:200])

    days.sort(key=lambda item: item["date"])
    pv7 = sum(day["pageviews"] for day in days)
    visits7 = sum(day["visits"] for day in days)
    last48 = sum(day["pageviews"] for day in days if day["date"] >= today - timedelta(days=1))
    latest = days[-1]["date"] if days else None

    traffic_problems, traffic_notes = assess_traffic_freshness(pv7, last48, latest, today)
    problems.extend(traffic_problems)
    notes.extend(traffic_notes)
    if pv7 and visits7 > pv7:
        notes.append(f"visits({visits7}) 高于 pageviews({pv7})，口径需人工确认")

    try:
        health = get_json(HEALTH)
        if not health.get("ok"):
            problems.append("运营后台 /api/health 未返回 ok")
    except urllib.error.URLError as exc:
        problems.append(f"运营后台健康检查不可达：{exc}")

    print(
        json.dumps(
            {
                "window": {"start": start, "end": end},
                "site_tag": SITE_TAG,
                "days_with_data": len(days),
                "pageviews_7d": pv7,
                "visits_7d": visits7,
                "pageviews_last_48h": last48,
                "latest_date": latest.isoformat() if latest else None,
                "problems": problems,
                "notes": notes,
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("## 访问统计看门狗\n")
            handle.write(f"- 窗口：{start} → {end}，有效日期 {len(days)} 天\n")
            handle.write(f"- 7 天浏览 **{pv7}** / 访问 **{visits7}**；最近 48h 浏览 **{last48}**\n")
            handle.write(f"- 结论：**{'异常' if problems else '正常'}**\n")
            for item in problems:
                handle.write(f"- ❌ {item}\n")
            for item in notes:
                handle.write(f"- ⚠️ {item}\n")

    if problems:
        for item in problems:
            print("::error::" + item)
        return 1
    print("analytics watchdog: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
