#!/usr/bin/env python3
"""Discover additional Italian AFAM conservatories on a weekly cadence.

The existing curated list remains the daily monitoring baseline. This script
uses Wikidata to find candidate institutions with official websites, probes
their admission pages, and adds only candidates that expose relevant admission
signals to data/conservatori_extra.json. The daily collector then includes the
approved registry in subsequent admission checks.

Only MAX_NEW institutions are added per run so a new batch can be reviewed."""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import scrape_conservatori as core

EXTRA_PATH = core.EXTRA_PATH
MAX_NEW = 6
MAX_PROBES = 14
USER_AGENT = "leo-conservatori-bot/1.0 (github.com/wl19971007-lgtm/leo)"
QUERIES = [
    "Conservatorio di musica",
    "Conservatorio statale di musica",
    "Istituto superiore di studi musicali",
    "Istituto statale superiore di studi musicali",
]
CITY_MAP = {
    "adria": "阿德里亚",
    "alessandria": "亚历山德里亚",
    "avellino": "阿韦利诺",
    "bari": "巴里",
    "benevento": "贝内文托",
    "bologna": "博洛尼亚",
    "bolzano": "博尔扎诺",
    "brescia": "布雷西亚",
    "cagliari": "卡利亚里",
    "caltanissetta": "卡尔塔尼塞塔",
    "campobasso": "坎波巴索",
    "castelfranco": "卡斯泰尔弗兰科",
    "catania": "卡塔尼亚",
    "cesena": "切塞纳",
    "como": "科莫",
    "cremona": "克雷莫纳",
    "cosenza": "科森扎",
    "cuneo": "库内奥",
    "fermo": "费尔莫",
    "ferrara": "费拉拉",
    "firenze": "佛罗伦萨",
    "foggia": "福贾",
    "frosinone": "弗罗西诺内",
    "genova": "热那亚",
    "l'aquila": "拉奎拉",
    "la spezia": "拉斯佩齐亚",
    "latina": "拉蒂纳",
    "lecce": "莱切",
    "lucca": "卢卡",
    "mantova": "曼托瓦",
    "matera": "马泰拉",
    "messina": "墨西拿",
    "milano": "米兰",
    "monopoli": "莫诺波利",
    "napoli": "那不勒斯",
    "novara": "诺瓦拉",
    "padova": "帕多瓦",
    "palermo": "巴勒莫",
    "parma": "帕尔马",
    "pavia": "帕维亚",
    "perugia": "佩鲁贾",
    "pesaro": "佩萨罗",
    "pescara": "佩斯卡拉",
    "piacenza": "皮亚琴察",
    "potenza": "波坦察",
    "ravenna": "拉文纳",
    "reggio calabria": "雷焦卡拉布里亚",
    "reggio emilia": "雷焦艾米利亚",
    "ribera": "里贝拉",
    "roma": "罗马",
    "rovigo": "罗维戈",
    "salerno": "萨莱诺",
    "sassari": "萨萨里",
    "siena": "锡耶纳",
    "taranto": "塔兰托",
    "teramo": "泰拉莫",
    "terni": "特尔尼",
    "torino": "都灵",
    "trapani": "特拉帕尼",
    "trento": "特伦托",
    "trieste": "的里雅斯特",
    "udine": "乌迪内",
    "venezia": "威尼斯",
    "verona": "维罗纳",
    "vibo valentia": "维博瓦伦蒂亚",
    "vicenza": "维琴察",
}
# Many conservatories are named after a composer, not a city: "Conservatorio
# Alfredo Casella" lives in L'Aquila and the page title often mentions no place.
NAME_CITY = {
    "casella": "拉奎拉",
    "cimarosa": "阿韦利诺",
    "sala": "贝内文托",
    "braga": "泰拉莫",
    "toscanini": "里贝拉",
    "scontrino": "特拉帕尼",
    "cilea": "雷焦卡拉布里亚",
    "perosi": "坎波巴索",
    "mascagni": "拉斯佩齐亚",
    "boccherini": "卢卡",
    "paganini": "热那亚",
    "rossini": "佩萨罗",
    "bellini": "卡塔尼亚",
    "donizetti": "贝加莫",
    "bottesini": "克雷莫纳",
    "galluppi": "卡坦扎罗",
    "tartini": "的里雅斯特",
    "maderna": "切塞纳",
}


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return json.load(urllib.request.urlopen(request, timeout=30))


def wikidata_candidates(term: str) -> list[str]:
    """Entity ids whose Italian label looks like a conservatory."""
    ids: list[str] = []
    for offset in (0, 50):
        query = urllib.parse.urlencode(
            {
                "action": "wbsearchentities",
                "search": term,
                "language": "it",
                "uselang": "it",
                "type": "item",
                "limit": 50,
                "offset": offset,
                "format": "json",
            }
        )
        for attempt in range(3):
            try:
                payload = get_json("https://www.wikidata.org/w/api.php?" + query)
                break
            except Exception as exc:  # 429 while hammering the API, transient 5xx
                print(f"  wikidata search retry ({type(exc).__name__})", flush=True)
                time.sleep(20 * (attempt + 1))
        else:
            return ids
        ids += [item["id"] for item in payload.get("search", [])]
        time.sleep(1.0)
    return ids


def official_sites(ids: list[str]) -> dict[str, str]:
    """Italian label -> official website, for entities that record P856."""
    out: dict[str, str] = {}
    for start in range(0, len(ids), 40):
        query = urllib.parse.urlencode(
            {
                "action": "wbgetentities",
                "ids": "|".join(ids[start : start + 40]),
                "props": "claims|labels",
                "languages": "it",
                "format": "json",
            }
        )
        try:
            payload = get_json("https://www.wikidata.org/w/api.php?" + query)
        except Exception:
            continue
        for entity in payload.get("entities", {}).values():
            label = entity.get("labels", {}).get("it", {}).get("value", "")
            claims = entity.get("claims", {}).get("P856") or []
            if not label or not claims:
                continue
            try:
                site = claims[0]["mainsnak"]["datavalue"]["value"]
            except (KeyError, IndexError, TypeError):
                continue
            if isinstance(site, str) and site.startswith("http"):
                out.setdefault(label, site)
        time.sleep(1.0)
    return out


def known_hosts() -> set[str]:
    hosts = set()
    for _, _, _, url in core.CONSERVATORIES:
        hosts.add(urlparse(url).netloc.removeprefix("www.").lower())
    if EXTRA_PATH.exists():
        try:
            payload = json.loads(EXTRA_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        for entry in payload.get("items", []):
            host = urlparse(entry.get("url") or "").netloc.removeprefix("www.").lower()
            if host:
                hosts.add(host)
    return hosts


def known_names() -> set[str]:
    """Distinctive part of every school name already scraped, to avoid a second address for it."""
    names = set()
    sources = list(core.CONSERVATORIES)
    if EXTRA_PATH.exists():
        try:
            payload = json.loads(EXTRA_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        for entry in payload.get("items", []):
            sources.append((0, entry.get("city") or "", entry.get("school") or "", entry.get("url") or ""))
    for _, _, school, _ in sources:
        label = re.sub(r"conservatorio|istituto|superiore|studi musicali|di musica|statale|d'italia", "", school.lower())
        label = core.clean_line(label)
        if len(label) > 4:
            names.add(label)
    return names


def city_for(text: str) -> str:
    lowered = text.lower()
    for name, label in sorted(CITY_MAP.items(), key=lambda pair: -len(pair[0])):
        if re.search(rf"\b{re.escape(name)}\b", lowered):
            return label
    for name, label in sorted(NAME_CITY.items(), key=lambda pair: -len(pair[0])):
        if re.search(rf"\b{re.escape(name)}\b", lowered):
            return label
    return "意大利"


def title_school(title: str) -> str:
    parts = [core.clean_line(part) for part in re.split(r"\s+[|–—]\s+|\s+-\s+", title) if part.strip()]
    for part in parts:
        if re.search(r"conservatorio|istituto", part, re.IGNORECASE):
            return part[:70]
    head = re.split(r"&#?\w+;", title, maxsplit=1)[0]
    return core.clean_line(head)[:70] or "Conservatorio"


def probe(host_url: str) -> dict | None:
    """Accept a site only when its admission page really carries the calendar."""
    try:
        status, title, lines, response = core.fetch_page(host_url)
    except Exception:
        return None
    if not status or status >= 400:
        return None
    body = core.clean_line(" ".join(lines[:400]))
    if not re.search(r"conservator", f"{title} {body}", re.IGNORECASE):
        return None
    deadlines, dates, requirements = core.signals(lines)
    url = host_url
    documents = core.collect_documents(response, host_url)
    for candidate in core.collect_candidates(response, host_url):
        try:
            sub_status, sub_title, sub_lines, sub_response = core.fetch_page(candidate)
        except Exception:
            continue
        if not sub_status or sub_status >= 400:
            continue
        sub = core.signals(sub_lines)
        if len(sub[0]) + len(sub[1]) + len(sub[2]) > len(deadlines) + len(dates) + len(requirements):
            deadlines, dates, requirements = sub
            documents = core.collect_documents(sub_response, candidate) or documents
            title = sub_title or title
            url = candidate
        if deadlines and dates:
            break
    if len(deadlines) + len(dates) + len(requirements) < 2:
        return None  # a live domain with no admission content is not a usable source
    return {
        "city": city_for(f"{title} {host_url}"),
        "school": title_school(title),
        "url": url,
        "homepage": host_url,
        "deadlines": len(deadlines),
        "dates": len(dates),
        "requirements": len(requirements),
        "documents": len(documents),
    }


def load_extra() -> dict:
    if EXTRA_PATH.exists():
        try:
            return json.loads(EXTRA_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"updated_at": None, "cursor": 0, "items": []}


def main() -> None:
    state = load_extra()
    cursor = int(state.get("cursor") or 0) % len(QUERIES)
    term = QUERIES[cursor]
    known = known_hosts()
    names = known_names()
    print(f"Querying Wikidata for “{term}” (cursor={cursor}), {len(known)} hosts already known", flush=True)

    found: list[dict] = []
    probed = 0
    for label, site in sorted(official_sites(wikidata_candidates(term)).items()):
        host = urlparse(site).netloc.removeprefix("www.").lower()
        if not host or host in known:
            continue
        if re.search(r"shcmusic|oberlin|gouv\.qc|conservatoire\.gouv", host, re.IGNORECASE):
            continue
        label_l = re.sub(r"conservatorio|istituto|superiore|studi musicali|di musica|statale", "", label.lower())
        label_l = core.clean_line(label_l)
        if any(name in label_l for name in names):
            continue  # same school, different address
        known.add(host)
        probed += 1
        root = f"https://{urlparse(site).netloc}/"
        result = probe(root)
        if result:
            result["wikidata_label"] = label
            result["source"] = "wikidata"
            found.append(result)
            print(f"  + {result['city']} {result['school']} → {result['url']}", flush=True)
        else:
            print(f"  · skipped {host}", flush=True)
        if len(found) >= MAX_NEW or probed >= MAX_PROBES:
            break

    items = state.get("items", [])
    start = max([int(entry.get("number") or 0) for entry in items] + [199]) + 1
    for offset, result in enumerate(found):
        items.append(
            {
                "number": start + offset,
                "city": result["city"],
                "school": result["school"],
                "url": result["url"],
                "homepage": result["homepage"],
                "source": result["source"],
                "wikidata_label": result["wikidata_label"],
                "added_at": datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds"),
            }
        )
    state.update(
        {
            "updated_at": datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="seconds"),
            "cursor": (cursor + 1) % len(QUERIES),
            "items": items,
        }
    )
    EXTRA_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXTRA_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Registered {len(found)} new conservator{'y' if len(found) == 1 else 'ies'}; registry now {len(items)}")


if __name__ == "__main__":
    main()
