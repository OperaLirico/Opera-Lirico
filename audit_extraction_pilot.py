#!/usr/bin/env python3
"""Five-source offline parser and endpoint-discovery pilot; never changes production policy."""
from __future__ import annotations
import hashlib, json, re, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree
from zoneinfo import ZoneInfo
from lxml import html as lxml_html
from scrapling import Selector

ROOT=Path(__file__).resolve().parent
AUDIT=ROOT/".github"/"audits"
SAMPLES=ROOT/"artifacts"/"p2-p4-html-samples"
ROME=ZoneInfo("Europe/Rome")
PILOT_IDS={"source-1","source-2","source-3","source-9","source-15"}
MAX_BYTES,DELAY=1_500_000,1.2
UA="ItaliaAuditionsResearchBot/1.0 (+https://github.com/wl19971007-lgtm/leo)"
SIGNALS={
 "vocal_roles":re.compile(r"soprano|mezzosoprano|contralto|contralti|tenore|baritono|basso",re.I),
 "deadline":re.compile(r"scadenz|entro il|termine|deadline|application",re.I),
 "audition":re.compile(r"audizion|concorso|bando|selezion|iscrizion",re.I),
 "dates":re.compile(r"\b(?:\d{1,2}[./-]\d{1,2}[./-]20\d{2}|20\d{2})\b",re.I),
 "application":re.compile(r"domanda|iscrizion|application|candidatura",re.I),
 "pdf":re.compile(r"\.pdf\b|bando|regolamento",re.I),
}
RELEVANT_TEXT=re.compile(r"bando|domanda|iscrizion|audizion|concorso|pdf|regolamento|candidatura|selezion|coro|cantant|soprano|tenore|bariton|bass[oi]|contralt",re.I)
RELEVANT_URL=re.compile(r"bando|domanda|iscrizion|audizion|concorso|pdf|regolamento|candidatura|selezion|coro|cantant|soprano|tenore|bariton|bass[oi]|contralt",re.I)
VOCAL_URL=re.compile(r"canto|cantant|soprano|tenore|baritono|basso|coro|audizion|concorso|bando|contralt",re.I)
REDIRECT_CODES=(301,302,303,307,308)

class SameHostRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        old=urllib.parse.urlsplit(req.full_url).netloc.lower()
        new=urllib.parse.urlsplit(newurl).netloc.lower()
        if old!=new:
            raise urllib.error.HTTPError(req.full_url,code,"Cross-host redirect requires robots check",headers,fp)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

OPENER=urllib.request.build_opener(SameHostRedirectHandler())

def now_iso():
    return datetime.now(ROME).isoformat(timespec="seconds")

def request_bytes(url):
    time.sleep(DELAY)
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    try:
        with OPENER.open(req,timeout=12) as res:
            body=res.read(MAX_BYTES+1)
            truncated=len(body)>MAX_BYTES
            return {"status":"too_large" if truncated else "ok","http_status":res.status,
                "final_url":res.geturl(),"content_type":res.headers.get("Content-Type"),
                "body":body[:MAX_BYTES],"truncated":truncated}
    except urllib.error.HTTPError as exc:
        location=exc.headers.get("Location") if exc.headers else None
        if exc.code in REDIRECT_CODES and location:
            return {"status":"cross_host_redirect","http_status":exc.code,
                "redirect_url":urllib.parse.urljoin(exc.geturl(),location),"body":b"",
                "final_url":exc.geturl(),"content_type":None,"truncated":False}
        return {"status":"restricted" if exc.code in (403,429) else "http_error",
            "http_status":exc.code,"final_url":exc.geturl(),
            "content_type":exc.headers.get("Content-Type") if exc.headers else None,
            "body":b"","truncated":False,"error":str(exc)[:240]}
    except Exception as exc:
        return {"status":"error","http_status":None,"final_url":url,"content_type":None,
            "body":b"","truncated":False,"error":f"{type(exc).__name__}: {str(exc)[:240]}"}

def robots_allows(url,text):
    parsed=urllib.parse.urlsplit(url); target=parsed.path or "/"
    if parsed.query: target+="?"+parsed.query
    groups=[]; agents=[]; rules=[]; saw_rule=False
    for raw in text.splitlines():
        line=raw.split("#",1)[0].strip()
        if not line or ":" not in line: continue
        key,value=[x.strip() for x in line.split(":",1)]; key=key.lower()
        if key=="user-agent":
            if saw_rule: groups.append((agents,rules)); agents=[]; rules=[]; saw_rule=False
            agents.append(value.lower())
        elif key in ("allow","disallow"):
            saw_rule=True
            if value: rules.append((key,value))
    if agents: groups.append((agents,rules))
    applicable=[]
    for group_agents,group_rules in groups:
        if "*" in group_agents or "italiaauditionsresearchbot" in group_agents:
            applicable.extend(group_rules)
    matches=[]
    for kind,rule in applicable:
        anchored=rule.endswith("$"); pattern=rule[:-1] if anchored else rule
        regex="^"+re.escape(pattern).replace(r"\*",".*")
        if anchored: regex+="$"
        if re.search(regex,target): matches.append((len(pattern.replace("*","")),kind))
    if not matches: return True
    longest=max(size for size,_ in matches)
    return any(kind=="allow" for size,kind in matches if size==longest)

def fetch_robots(origin):
    response=request_bytes(origin.rstrip("/")+"/robots.txt")
    if response["status"]=="cross_host_redirect":
        response=request_bytes(response["redirect_url"])
    response["robots_origin"]=origin
    return response

def permitted_fetch(url,source_url,source_robots,max_redirects=2):
    current=url
    for _ in range(max_redirects+1):
        source_host=urllib.parse.urlsplit(source_url).netloc.lower()
        target=urllib.parse.urlsplit(current)
        target_origin=f"{target.scheme}://{target.netloc}"
        if target.netloc.lower()==source_host:
            policy=source_robots
        else:
            policy=fetch_robots(target_origin)
        policy_status=policy["status"]
        if policy_status!="ok" and policy["http_status"]!=404:
            return {"status":"robots_unavailable","http_status":policy["http_status"],
                    "final_url":current,"body":b"","robots_status":policy_status}
        if policy_status=="ok":
            rules=policy["body"].decode("utf-8","replace")
            if not robots_allows(current,rules):
                return {"status":"robots_disallowed","http_status":None,
                        "final_url":current,"body":b"","robots_status":"ok"}
        response=request_bytes(current)
        if response["status"]=="cross_host_redirect":
            current=response["redirect_url"]
            continue
        response["robots_status"]=policy_status
        return response
    return {"status":"redirect_limit","http_status":None,"final_url":current,"body":b""}

def parse_sitemap(data):
    try: root=ElementTree.fromstring(data)
    except ElementTree.ParseError: return {"kind":"invalid_xml","locs":[]}
    kind=root.tag.rsplit("}",1)[-1].lower()
    locs=[n.text.strip() for n in root.iter() if n.tag.rsplit("}",1)[-1].lower()=="loc" and n.text]
    return {"kind":kind,"locs":locs}

def feed_summary(data):
    try: root=ElementTree.fromstring(data)
    except ElementTree.ParseError: return {"kind":"invalid_xml","entry_count":0,"relevant_entry_count":0,"relevant_titles":[]}
    kind=root.tag.rsplit("}",1)[-1].lower()
    entries=[n for n in root.iter() if n.tag.rsplit("}",1)[-1].lower() in ("item","entry")]
    relevant=[]
    for entry in entries:
        parts=[]; title=""
        for node in entry.iter():
            value=" ".join(" ".join(node.itertext()).split())
            if node.tag.rsplit("}",1)[-1].lower()=="title" and value: title=value
            if value: parts.append(value)
        joined=" ".join(parts)
        if SIGNALS["vocal_roles"].search(joined) or SIGNALS["audition"].search(joined):
            relevant.append(title or joined[:160])
    return {"kind":kind,"entry_count":len(entries),"relevant_entry_count":len(relevant),"relevant_titles":relevant[:10]}

def normalize(text):
    return re.sub(r"\s+"," ",text or "").strip()

def metrics(text,relevant_anchors):
    normalized=normalize(text)
    labels=sorted({x["text"] for x in relevant_anchors if x.get("text")})
    targets=sorted({x["url"] for x in relevant_anchors if x.get("url")})
    retained_labels={label for label in labels if len(label)>=3 and label.casefold() in normalized.casefold()}
    retained_targets={url for url in targets if url.casefold() in normalized.casefold()}
    return {"characters":len(normalized),
        "signals":{key:bool(pattern.search(normalized)) for key,pattern in SIGNALS.items()},
        "relevant_dom_link_labels_available":len(labels),
        "relevant_dom_link_labels_retained_in_text":len(retained_labels),
        "relevant_link_targets_available":len(targets),
        "relevant_link_targets_retained_in_text":len(retained_targets)}

def compare(html_bytes,url):
    started=time.perf_counter(); sel=Selector(content=html_bytes,url=url)
    scrap_text=sel.get_all_text(separator="\n") or ""; scrap_seconds=time.perf_counter()-started
    started=time.perf_counter(); dom=lxml_html.fromstring(html_bytes,base_url=url)
    lxml_text="\n".join(x.strip() for x in dom.xpath("//body//text()[normalize-space()]") if x.strip())
    lxml_seconds=time.perf_counter()-started
    anchors=[]
    for node in dom.xpath("//a[@href]"):
        href=urllib.parse.urljoin(url,node.get("href")); label=normalize(" ".join(node.itertext()))
        if href.startswith(("http://","https://")): anchors.append({"text":label[:240],"url":href})
    relevant_labels=sorted({x["text"] for x in anchors if x["text"] and RELEVANT_TEXT.search(x["text"])})
    relevant_text_anchors=[x for x in anchors if x["text"] and RELEVANT_TEXT.search(x["text"])]
    relevant_url_anchors=[x for x in anchors if RELEVANT_URL.search(x["url"])]
    relevant_anchors=[x for x in anchors if (x["text"] and RELEVANT_TEXT.search(x["text"])) or RELEVANT_URL.search(x["url"])]
    title_nodes=dom.xpath("//title/text()"); title=normalize(title_nodes[0]) if title_nodes else ""
    try:
        import trafilatura
        decoded=lxml_html.tostring(dom,encoding="unicode")
        started=time.perf_counter()
        traf_plain=trafilatura.extract(decoded,include_links=True,include_tables=True,favor_recall=True) or ""
        plain_seconds=time.perf_counter()-started
        started=time.perf_counter()
        traf_md=trafilatura.extract(decoded,output_format="markdown",include_links=True,include_tables=True,favor_recall=True) or ""
        md_seconds=time.perf_counter()-started
        traf_status="ok" if traf_plain else "empty"
    except Exception as exc:
        traf_plain=traf_md=""; plain_seconds=md_seconds=None; traf_status=f"error:{type(exc).__name__}"
    markdown_links=re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)",traf_md)
    markdown_relevant_links=[(label,target) for label,target in markdown_links
        if RELEVANT_TEXT.search(label) or RELEVANT_URL.search(target)]
    relevant_targets={x["url"] for x in relevant_anchors}
    markdown_retained_targets={target for _,target in markdown_relevant_links if target in relevant_targets}
    return {
        "title":title,
        "dom_structure":{"anchor_count":len(anchors),"relevant_text_anchor_count":len(relevant_text_anchors),
            "relevant_url_anchor_count":len(relevant_url_anchors),
            "relevant_anchor_examples":relevant_text_anchors[:30],
            "relevant_url_examples":relevant_url_anchors[:30],
            "list_item_count":len(dom.xpath("//li")),"heading_count":len(dom.xpath("//h1|//h2|//h3")),
            "table_count":len(dom.xpath("//table"))},
        "scrapling":{"runtime_seconds":round(scrap_seconds,4),**metrics(scrap_text,relevant_anchors)},
        "lxml_full_text":{"runtime_seconds":round(lxml_seconds,4),**metrics(lxml_text,relevant_anchors)},
        "trafilatura_plain":{"status":traf_status,
            "runtime_seconds":round(plain_seconds,4) if plain_seconds is not None else None,
            **metrics(traf_plain,relevant_anchors)},
        "trafilatura_markdown":{"runtime_seconds":round(md_seconds,4) if md_seconds is not None else None,
            "characters":len(normalize(traf_md)),"markdown_link_count":len(markdown_links),
            "markdown_relevant_link_count":len(markdown_relevant_links),
            "relevant_dom_link_targets_available":len(relevant_targets),
            "relevant_dom_link_targets_retained":len(markdown_retained_targets)},
    }

def sitemap_result(url,source_url,robots):
    response=permitted_fetch(url,source_url,robots)
    parsed=parse_sitemap(response["body"]) if response["status"]=="ok" else {"kind":"unavailable","locs":[]}
    locs=parsed["locs"]
    result={"url":url,"status":response["status"],"http_status":response["http_status"],
        "sitemap_kind":parsed["kind"],"loc_count":len(locs),
        "vocal_or_audition_url_count":sum(bool(VOCAL_URL.search(loc)) for loc in locs),
        "url_examples":[loc for loc in locs if VOCAL_URL.search(loc)][:12],
        "robots_status":response.get("robots_status")}
    if parsed["kind"]=="sitemapindex":
        children=[]
        for child_url in locs[:3]:
            child_response=permitted_fetch(child_url,source_url,robots)
            child_map=parse_sitemap(child_response["body"]) if child_response["status"]=="ok" else {"kind":"unavailable","locs":[]}
            child_locs=child_map["locs"]
            children.append({"url":child_url,"status":child_response["status"],
                "http_status":child_response["http_status"],"sitemap_kind":child_map["kind"],
                "loc_count":len(child_locs),
                "vocal_or_audition_url_count":sum(bool(VOCAL_URL.search(loc)) for loc in child_locs),
                "url_examples":[loc for loc in child_locs if VOCAL_URL.search(loc)][:12]})
        result["sampled_child_sitemaps"]=children
    return result

def api_root_summary(url,source_url,robots):
    response=permitted_fetch(url,source_url,robots)
    result={"url":url,"status":response["status"],"http_status":response["http_status"]}
    if response["status"]!="ok": return result
    try:
        payload=json.loads(response["body"].decode("utf-8","replace"))
        routes=payload.get("routes",{})
        route_names=list(routes.keys()) if isinstance(routes,dict) else []
        result.update({"namespace_count":len(payload.get("namespaces",[])),
            "namespaces":payload.get("namespaces",[])[:20],"route_count":len(route_names),
            "content_routes":[x for x in route_names if re.search(r"wp/v2/(posts|pages|media|types|search)",x,re.I)][:20],
            "custom_routes":[x for x in route_names if re.search(r"audition|bando|coro|canto",x,re.I)][:20]})
    except Exception:
        result["json_parse"]="invalid_or_non_json"
    return result

def discovery(url,html_bytes,robots):
    parts=urllib.parse.urlsplit(url); origin=f"{parts.scheme}://{parts.netloc}"
    dom=lxml_html.fromstring(html_bytes,base_url=url)
    feeds=[]; api_links=[]
    for node in dom.xpath("//link[@href]"):
        rel=" ".join(node.get("rel","").lower().split()); typ=(node.get("type") or "").lower()
        href=urllib.parse.urljoin(url,node.get("href"))
        if "alternate" in rel and ("rss" in typ or "atom" in typ): feeds.append(href)
        if "api.w.org" in rel: api_links.append(href)
    sitemap_candidates=[]
    if robots["status"]=="ok":
        txt=robots["body"].decode("utf-8","replace")
        sitemap_candidates=[line.split(":",1)[1].strip() for line in txt.splitlines()
            if line.lower().startswith("sitemap:") and ":" in line]
    if not sitemap_candidates:
        sitemap_candidates=[origin+"/sitemap.xml",origin+"/wp-sitemap.xml",origin+"/sitemap_index.xml"]
    sitemap_results=[]
    for sm in sitemap_candidates[:3]:
        sitemap_results.append(sitemap_result(urllib.parse.urljoin(origin+"/",sm),url,robots))
    feed_results=[]
    for feed_url in sorted(set(feeds))[:3]:
        response=permitted_fetch(feed_url,url,robots)
        summary=feed_summary(response["body"]) if response["status"]=="ok" else {
            "kind":"unavailable","entry_count":0,"relevant_entry_count":0,"relevant_titles":[]}
        feed_results.append({"url":feed_url,"status":response["status"],"http_status":response["http_status"],
            "robots_status":response.get("robots_status"),**summary})
    api_results=[api_root_summary(api_url,url,robots) for api_url in sorted(set(api_links))[:1]]
    return {"robots":{"status":robots["status"],"http_status":robots["http_status"],
            "robots_url":robots.get("final_url")},
        "sitemaps":sitemap_results,"advertised_feeds":feed_results,"advertised_public_api_roots":api_results}

def main():
    policies=json.loads((ROOT/"data/source_fetch_policies.json").read_text(encoding="utf-8"))
    sources={x["source_id"]:x for x in policies["entries"]}
    AUDIT.mkdir(parents=True,exist_ok=True); SAMPLES.mkdir(parents=True,exist_ok=True)
    report={"generated_at":now_iso(),"scope":"Five high-value first-party vocal sources.",
        "pilot_source_ids":sorted(PILOT_IDS),"production_changes":False,"strategy_status":"evaluation_only","items":[],
        "limitations":["robots.txt is checked before page, sitemap, feed and public API requests, including cross-host redirects.",
            "Only page-advertised RSS/Atom and explicit public API links are inspected; no guessed API endpoint is queried.",
            "403/429, login restrictions and unreadable robots policies are recorded and not bypassed.",
            "Parser counts and keyword signals are coverage proxies, not ground-truth accuracy.",
            "All parsers receive identical captured HTML bytes; no production policy is promoted automatically.",
            "Sitemap indexes are sampled to at most three child sitemaps per source; this is not a complete recursive crawl."]}
    for sid in sorted(PILOT_IDS):
        src=sources.get(sid)
        if not src: report["items"].append({"source_id":sid,"status":"missing_policy"}); continue
        parts=urllib.parse.urlsplit(src["url"]); origin=f"{parts.scheme}://{parts.netloc}"
        robots=fetch_robots(origin)
        robots_text=robots["body"].decode("utf-8","replace") if robots["status"]=="ok" else ""
        robots_unavailable=robots["status"]!="ok" and robots["http_status"]!=404
        blocked=robots_unavailable or (robots["status"]=="ok" and not robots_allows(src["url"],robots_text))
        item={"source_id":sid,"source_name":src["source_name"],"url":src["url"],
            "robots_status":robots["status"],"robots_http_status":robots["http_status"]}
        if blocked:
            item["fetch_status"]="robots_disallowed_or_unavailable"
            item["strategy_recommendation"]="skip_page_fetch_and_review_robots_policy"
            report["items"].append(item); continue
        fetched=permitted_fetch(src["url"],src["url"],robots)
        item.update({"fetch_status":fetched["status"],"http_status":fetched["http_status"],
            "final_url":fetched["final_url"],"content_type":fetched.get("content_type"),
            "truncated":fetched.get("truncated",False),"error":fetched.get("error")})
        if fetched["status"]!="ok" or not fetched["body"]:
            item["strategy_recommendation"]="retain_current_and_review_access"
            report["items"].append(item); continue
        body=fetched["body"]; sample=SAMPLES/f"{sid}.html"; sample.write_bytes(body)
        item["raw_snapshot"]={"artifact_path":str(sample.relative_to(ROOT)),"bytes":len(body),
            "sha256":hashlib.sha256(body).hexdigest(),"captured_at":now_iso()}
        try:
            item["discovery"]=discovery(src["url"],body,robots)
            item["parsers"]=compare(body,src["url"])
            item["strategy_recommendation"]="manual_review_required"
        except Exception as exc:
            item["analysis_error"]=f"{type(exc).__name__}: {str(exc)[:240]}"
            item["strategy_recommendation"]="retain_current_and_review_parser_error"
        report["items"].append(item)
    (AUDIT/"extraction-pilot-latest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    captured=sum(bool(x.get("raw_snapshot")) for x in report["items"])
    feeds=[f for x in report["items"] for f in x.get("discovery",{}).get("advertised_feeds",[])]
    api=[a for x in report["items"] for a in x.get("discovery",{}).get("advertised_public_api_roots",[])]
    lines=["# P2/P4 source and extraction pilot","",f"- Generated: {report['generated_at']} (Europe/Rome)",
        f"- Pages captured: {captured}/5",f"- Advertised feeds checked: {len(feeds)}",
        f"- Feeds with vocal/audition entries: {sum(f.get('relevant_entry_count',0)>0 for f in feeds)}",
        f"- Explicit public API roots checked: {len(api)}",
        "- Production strategy changes: none","- Parser comparisons use identical HTML bytes.",
        "- Metrics are coverage proxies, not accuracy scores; raw HTML is uploaded as a 30-day artifact.",""]
    for item in report["items"]:
        lines += [f"## {item.get('source_name',item['source_id'])}","",f"- URL: {item.get('url','missing')}",
            f"- Fetch: {item.get('fetch_status',item.get('status'))}; HTTP {item.get('http_status')}"]
        if item.get("raw_snapshot"):
            snap=item["raw_snapshot"]; lines.append(f"- Snapshot: {snap['bytes']} bytes; SHA-256 {snap['sha256']}")
        d=item.get("discovery")
        if d:
            lines.append(f"- robots.txt: {d['robots']['status']} HTTP {d['robots']['http_status']}")
            for sm in d["sitemaps"]:
                lines.append(f"- Sitemap: {sm['url']} — {sm['status']} HTTP {sm['http_status']}; type={sm['sitemap_kind']}; locs={sm['loc_count']}; vocal/audition URLs={sm['vocal_or_audition_url_count']}")
                for child in sm.get("sampled_child_sitemaps",[]):
                    lines.append(f"  - Child sitemap: {child['url']} — {child['status']} HTTP {child['http_status']}; locs={child['loc_count']}; vocal/audition URLs={child['vocal_or_audition_url_count']}")
            for feed in d["advertised_feeds"]:
                lines.append(f"- Feed: {feed['url']} — {feed['status']} HTTP {feed['http_status']}; entries={feed['entry_count']}; relevant entries={feed['relevant_entry_count']}")
            for api_item in d["advertised_public_api_roots"]:
                lines.append(f"- Public API root: {api_item['url']} — {api_item['status']} HTTP {api_item['http_status']}; routes={api_item.get('route_count',0)}; relevant routes={len(api_item.get('content_routes',[]))+len(api_item.get('custom_routes',[]))}")
        p=item.get("parsers")
        if p:
            dom=p["dom_structure"]
            lines.append(f"- DOM: {dom['anchor_count']} links; relevant text labels={dom['relevant_text_anchor_count']}; relevant URLs={dom['relevant_url_anchor_count']}; list items={dom['list_item_count']}; headings={dom['heading_count']}; tables={dom['table_count']}")
            for name in ("scrapling","lxml_full_text","trafilatura_plain"):
                m=p[name]; lines.append(f"- {name}: {m['characters']} chars; signals={sum(m['signals'].values())}/6; relevant labels retained={m['relevant_dom_link_labels_retained_in_text']}/{m['relevant_dom_link_labels_available']}; href targets in plain text={m['relevant_link_targets_retained_in_text']}/{m['relevant_link_targets_available']}; runtime={m['runtime_seconds']}s")
            md=p["trafilatura_markdown"]
            lines.append(f"- trafilatura_markdown: {md['characters']} chars; links={md['markdown_link_count']}; relevant links={md['markdown_relevant_link_count']}; exact relevant hrefs retained={md['relevant_dom_link_targets_retained']}/{md['relevant_dom_link_targets_available']}; runtime={md['runtime_seconds']}s")
        lines.append(f"- Recommendation: {item.get('strategy_recommendation')}")
        if item.get("analysis_error"): lines.append(f"- Analysis error: {item['analysis_error']}")
        lines.append("")
    lines += ["## Limitations",""]+["- "+x for x in report["limitations"]]
    (AUDIT/"extraction-pilot-latest.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"pages_captured":captured,"feeds_checked":len(feeds),
        "feeds_with_relevant_entries":sum(f.get("relevant_entry_count",0)>0 for f in feeds),
        "api_roots_checked":len(api),"items":[{"source_id":x["source_id"],"status":x.get("fetch_status",x.get("status")),
            "http_status":x.get("http_status"),"sha256":x.get("raw_snapshot",{}).get("sha256"),
            "analysis_error":x.get("analysis_error")} for x in report["items"]]},ensure_ascii=False))

if __name__=="__main__":
    main()
