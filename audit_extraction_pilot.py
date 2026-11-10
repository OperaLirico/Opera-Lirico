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
import trafilatura

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / ".github" / "audits"
SAMPLES = ROOT / "artifacts" / "p2-p4-html-samples"
ROME = ZoneInfo("Europe/Rome")
PILOT_IDS = {"source-1", "source-2", "source-3", "source-9", "source-15"}
MAX_BYTES, DELAY = 1_500_000, 1.2
UA = "ItaliaAudizioniResearchBot/1.0 (+https://github.com/wl19971007-lgtm/leo)"
SIGNALS = {
 "vocal_roles": re.compile(r"soprano|mezzosoprano|contralto|tenore|baritono|basso", re.I),
 "deadline": re.compile(r"scadenz|entro il|termine|deadline|application", re.I),
 "audition": re.compile(r"audizion|concorso|bando|selezion|iscrizion", re.I),
 "dates": re.compile(r"\b(?:\d{1,2}[./-]\d{1,2}[./-]20\d{2}|20\d{2})\b", re.I),
 "application": re.compile(r"domanda|iscrizion|application|candidatura", re.I),
 "pdf": re.compile(r"\.pdf\b|bando|regolamento", re.I),
}

def now_iso():
 return datetime.now(ROME).isoformat(timespec="seconds")

def request_bytes(url):
 req = urllib.request.Request(url, headers={"User-Agent": UA})
 try:
  with urllib.request.urlopen(req, timeout=20) as res:
   body = res.read(MAX_BYTES + 1)
   truncated = len(body) > MAX_BYTES
   return {"status":"too_large" if truncated else "ok", "http_status":res.status,
    "final_url":res.geturl(), "content_type":res.headers.get("Content-Type"),
    "body":body[:MAX_BYTES], "truncated":truncated}
 except urllib.error.HTTPError as exc:
  return {"status":"restricted" if exc.code in (403,429) else "http_error",
   "http_status":exc.code, "final_url":exc.geturl(),
   "content_type":exc.headers.get("Content-Type") if exc.headers else None,
   "body":b"", "truncated":False, "error":str(exc)[:240]}
 except Exception as exc:
  return {"status":"error", "http_status":None, "final_url":url, "content_type":None,
   "body":b"", "truncated":False, "error":f"{type(exc).__name__}: {str(exc)[:240]}"}

def parse_sitemap(data):
 try: root = ElementTree.fromstring(data)
 except ElementTree.ParseError: return 0
 return sum(1 for n in root.iter() if n.tag.endswith("loc") and n.text)

def metrics(text, links):
 normalized = re.sub(r"\s+", " ", text or "").strip()
 return {"characters":len(normalized),
  "signals":{k:bool(v.search(normalized)) for k,v in SIGNALS.items()},
  "relevant_link_labels":sum(bool(re.search(r"bando|domanda|iscrizion|audizion|concorso|pdf|regolamento",x["text"],re.I)) for x in links)}

def compare(html_bytes, url):
 started = time.perf_counter()
 sel = Selector(content=html_bytes, url=url)
 scrap_text = sel.get_all_text(separator="\n") or ""
 scrap_seconds = time.perf_counter() - started
 started = time.perf_counter()
 dom = lxml_html.fromstring(html_bytes, base_url=url)
 lxml_text = "\n".join(x.strip() for x in dom.xpath("//body//text()[normalize-space()]") if x.strip())
 lxml_seconds = time.perf_counter() - started
 links = []
 for node in dom.xpath("//a[@href]"):
  href = urllib.parse.urljoin(url,node.get("href"))
  label = " ".join(" ".join(node.itertext()).split())
  if href.startswith(("http://","https://")): links.append({"text":label[:240],"url":href})
 try:
  started = time.perf_counter()
  decoded_html = lxml_html.tostring(dom, encoding="unicode")
  traf_text = trafilatura.extract(decoded_html,include_links=True,include_tables=True,favor_recall=True) or ""
  traf_seconds = time.perf_counter() - started
  traf_status = "ok" if traf_text else "empty"
 except Exception as exc:
  traf_text,traf_status,traf_seconds = "",f"error:{type(exc).__name__}",None
 relevant = [x for x in links if re.search(r"bando|domanda|iscrizion|audizion|concorso|pdf|regolamento",x["text"]+" "+x["url"],re.I)]
 return {"scrapling":{"runtime_seconds":round(scrap_seconds,4),**metrics(scrap_text,links)},
  "lxml_full_text":{"runtime_seconds":round(lxml_seconds,4),**metrics(lxml_text,links)},
  "trafilatura":{"status":traf_status,"runtime_seconds":round(traf_seconds,4) if traf_seconds is not None else None,**metrics(traf_text,links)},
  "dom_link_count":len(links),"relevant_links":relevant[:40],
  "comparison_note":"Coverage proxies only, not precision/recall ground truth; manually review actual notice facts."}

def robots_allows(url, robots_text):
 path=urllib.parse.urlsplit(url).path or "/"
 groups=[]; agents=[]; rules=[]; saw_rule=False
 for raw in robots_text.splitlines():
  line=raw.split("#",1)[0].strip()
  if not line or ":" not in line: continue
  key,value=[x.strip() for x in line.split(":",1)]
  key=key.lower(); value=value.strip()
  if key=="user-agent":
   if saw_rule:
    groups.append((agents,rules)); agents=[]; rules=[]; saw_rule=False
   agents.append(value.lower())
  elif key in ("allow","disallow"):
   saw_rule=True
   if value: rules.append((key,value))
 if agents: groups.append((agents,rules))
 applicable=[]
 for group_agents,group_rules in groups:
  if "*" in group_agents or "italiaauditionsresearchbot" in group_agents:
   applicable.extend(group_rules)
 matches=[(len(rule),kind) for kind,rule in applicable if path.startswith(rule)]
 if not matches: return True
 longest=max(length for length,_ in matches)
 return any(kind=="allow" for length,kind in matches if length==longest)

def discovery(url, html_bytes, robots):
 parts=urllib.parse.urlsplit(url); origin=f"{parts.scheme}://{parts.netloc}"
 root=lxml_html.fromstring(html_bytes,base_url=url)
 feeds=[]
 for node in root.xpath("//link[@href]"):
  rel=" ".join(node.get("rel","").lower().split()); typ=(node.get("type") or "").lower()
  if "alternate" in rel and ("rss" in typ or "atom" in typ): feeds.append(urllib.parse.urljoin(url,node.get("href")))
 candidates=[]
 if robots["status"]=="ok":
  txt=robots["body"].decode("utf-8","replace")
  candidates=[line.split(":",1)[1].strip() for line in txt.splitlines() if line.lower().startswith("sitemap:") and ":" in line]
 if not candidates: candidates=[origin+"/sitemap.xml",origin+"/wp-sitemap.xml"]
 sitemaps=[]
 for sm in candidates[:2]:
  time.sleep(DELAY); r=request_bytes(urllib.parse.urljoin(origin+"/",sm))
  sitemaps.append({"url":sm,"status":r["status"],"http_status":r["http_status"],"loc_count":parse_sitemap(r["body"]) if r["status"]=="ok" else 0})
 root=lxml_html.fromstring(html_bytes,base_url=url)
 feeds=[]
 for node in root.xpath("//link[@href]"):
  rel=" ".join(node.get("rel","").lower().split()); typ=(node.get("type") or "").lower()
  if "alternate" in rel and ("rss" in typ or "atom" in typ): feeds.append(urllib.parse.urljoin(url,node.get("href")))
 feed_results=[]
 for feed in sorted(set(feeds))[:2]:
  time.sleep(DELAY); r=request_bytes(feed)
  feed_results.append({"url":feed,"status":r["status"],"http_status":r["http_status"]})
 return {"robots":{"status":robots["status"],"http_status":robots["http_status"]},"sitemaps":sitemaps,"advertised_feeds":feed_results}

def main():
 policies=json.loads((ROOT/"data/source_fetch_policies.json").read_text(encoding="utf-8"))
 source_map={x["source_id"]:x for x in policies["entries"]}
 AUDIT.mkdir(parents=True,exist_ok=True); SAMPLES.mkdir(parents=True,exist_ok=True)
 report={"generated_at":now_iso(),"scope":"Five high-value first-party vocal sources.",
  "pilot_source_ids":sorted(PILOT_IDS),"production_changes":False,"strategy_status":"evaluation_only","items":[],
  "limitations":["robots.txt/sitemap availability does not prove relevant notices are present.",
   "Only advertised RSS/Atom feeds are checked.","403/429 are recorded, never bypassed.",
   "Parser counts and keyword signals are proxies, not ground-truth accuracy.",
   "All parsers receive identical captured HTML bytes; no production policy is promoted automatically."]}
 for sid in sorted(PILOT_IDS):
  src=source_map.get(sid)
  if not src: report["items"].append({"source_id":sid,"status":"missing_policy"}); continue
  parts=urllib.parse.urlsplit(src["url"]); origin=f"{parts.scheme}://{parts.netloc}"
  robots=request_bytes(origin+"/robots.txt")
  robots_text=robots["body"].decode("utf-8","replace") if robots["status"]=="ok" else ""
  robots_unavailable=(robots["status"]!="ok" and robots["http_status"]!=404)
  blocked=(robots_unavailable or
   (robots["status"]=="ok" and not robots_allows(src["url"],robots_text)))
  item={"source_id":sid,"source_name":src["source_name"],"url":src["url"],
   "robots_status":robots["status"],"robots_http_status":robots["http_status"]}
  if blocked:
   item["fetch_status"]="robots_disallowed_or_unavailable"
   item["strategy_recommendation"]="skip_page_fetch_and_review_robots_policy"
   report["items"].append(item); time.sleep(DELAY); continue
  time.sleep(DELAY)
  fetched=request_bytes(src["url"])
  item.update({"fetch_status":fetched["status"],"http_status":fetched["http_status"],
   "final_url":fetched["final_url"],"content_type":fetched["content_type"],
   "truncated":fetched["truncated"],"error":fetched.get("error")})
  if fetched["status"]!="ok" or not fetched["body"]:
   item["strategy_recommendation"]="retain_current_and_review_access"
   report["items"].append(item); time.sleep(DELAY); continue
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
  report["items"].append(item); time.sleep(DELAY)
 (AUDIT/"extraction-pilot-latest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 lines=["# P2/P4 source and extraction pilot","",f"- Generated: {report['generated_at']} (Europe/Rome)",
  f"- Pages captured: {sum(bool(x.get('raw_snapshot')) for x in report['items'])}/5",
  "- Production strategy changes: none","- Parser comparisons use identical HTML bytes.",
  "- Metrics are coverage proxies, not accuracy scores; raw HTML is uploaded as a 30-day artifact.",""]
 for item in report["items"]:
  lines += [f"## {item.get('source_name',item['source_id'])}","",f"- URL: {item.get('url','missing')}",
   f"- Fetch: {item.get('fetch_status',item.get('status'))}; HTTP {item.get('http_status')}"]
  if item.get("raw_snapshot"):
   snap=item["raw_snapshot"]; lines.append(f"- Snapshot: {snap['bytes']} bytes; SHA-256 {snap['sha256']}")
  if item.get("discovery"):
   d=item["discovery"]; lines.append(f"- robots.txt: {d['robots']['status']} HTTP {d['robots']['http_status']}")
   for sm in d["sitemaps"]: lines.append(f"- Sitemap: {sm['url']} — {sm['status']} HTTP {sm['http_status']}, {sm['loc_count']} loc")
   for feed in d["advertised_feeds"]: lines.append(f"- Feed: {feed['url']} — {feed['status']} HTTP {feed['http_status']}")
  if item.get("parsers"):
   for name in ("scrapling","lxml_full_text","trafilatura"):
    m=item["parsers"][name]; lines.append(f"- {name}: {m.get('characters',0)} chars; signals {sum(m.get('signals',{}).values())}/6; relevant link labels {m.get('relevant_link_labels',0)}")
  lines.append(f"- Recommendation: {item.get('strategy_recommendation')}")
  if item.get("analysis_error"): lines.append(f"- Analysis error: {item['analysis_error']}")
  lines.append("")
 lines += ["## Limitations",""]+["- "+x for x in report["limitations"]]
 (AUDIT/"extraction-pilot-latest.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(json.dumps({"pages_captured":sum(bool(x.get("raw_snapshot")) for x in report["items"]),
  "items":[{"source_id":x["source_id"],"status":x.get("fetch_status",x.get("status")),
   "http_status":x.get("http_status"),"sha256":x.get("raw_snapshot",{}).get("sha256"),
   "analysis_error":x.get("analysis_error")} for x in report["items"]]},ensure_ascii=False))

if __name__=="__main__": main()
