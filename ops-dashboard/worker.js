const SESSION_COOKIE = "__Host-opera_ops";
const SESSION_TTL_SECONDS = 8 * 60 * 60;
const loginAttempts = new Map();

const PAGE = String.raw`<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Opera Lirico · 运营后台</title>
<style>
:root{color-scheme:light;--ink:#17231e;--muted:#66736c;--paper:#f4f1e8;--card:#fffdf8;--line:#ddd7c9;--green:#173d32;--gold:#98703d}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1080px;margin:0 auto;padding:36px 22px 60px}.top{display:flex;justify-content:space-between;align-items:center;gap:14px;margin-bottom:28px}
.brand{font:600 22px Georgia,serif}.sub{color:var(--muted);font-size:12px;letter-spacing:.12em}
h1{font:600 clamp(28px,5vw,42px) Georgia,serif;margin:8px 0 4px}.intro{color:var(--muted);margin:0 0 26px}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.card{background:var(--card);border:1px solid var(--line);border-radius:15px;padding:19px;min-width:0}
.kicker{color:var(--gold);font-size:11px;letter-spacing:.13em}.value{font:600 34px Georgia,serif;margin:7px 0 2px}.hint{font-size:12px;color:var(--muted)}
.section{margin-top:22px}.section h2{font:600 22px Georgia,serif;margin:0 0 12px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:15px;padding:20px}
.bars{display:flex;align-items:end;gap:5px;height:150px;padding-top:12px}.bar-wrap{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:end;align-items:center;height:100%;gap:5px}
.bar{width:100%;max-width:22px;min-height:2px;background:#557b6b;border-radius:4px 4px 0 0}.bar-label{font-size:9px;color:var(--muted);white-space:nowrap}
.drafts{display:grid;gap:0}.draft{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--line)}.draft:last-child{border:0}
a{color:var(--green)}.draft small{display:block;color:var(--muted);font-size:11px}.empty,.error{color:var(--muted);padding:12px 0}.error{color:#9a3d32}
button{font:inherit;cursor:pointer;border:1px solid var(--line);border-radius:999px;padding:8px 14px;background:var(--card);color:var(--ink)}
button.primary{background:var(--green);border-color:var(--green);color:white}
.login{max-width:420px;margin:12vh auto;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:28px}
input{width:100%;padding:12px 14px;border:1px solid var(--line);border-radius:10px;font:inherit;margin:10px 0 14px}
.notice{font-size:12px;color:var(--muted);margin-top:14px}.status{font-size:12px;color:var(--muted);margin:12px 0}
@media(max-width:760px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.top{align-items:flex-start}}
@media(max-width:420px){.grid{grid-template-columns:1fr 1fr}.card{padding:14px}.value{font-size:29px}}
</style></head><body>
<div id="loginView" class="login" hidden>
<div class="sub">OPERA LIRICO · PRIVATE</div><h1>运营后台</h1><p class="intro">请输入后台访问密码。</p>
<form id="loginForm"><label for="password">访问密码</label><input id="password" type="password" autocomplete="current-password" required><button class="primary" type="submit">登录</button></form>
<p id="loginError" class="error" role="alert"></p><p class="notice">仅授权人员可访问。此页面不会保存你的密码。</p>
</div>
<main id="appView" hidden>
<div class="top"><div><div class="brand">Opera Lirico</div><div class="sub">PRIVATE OPERATIONS DASHBOARD</div></div><div style="display:flex;gap:8px;align-items:center"><button id="refresh">刷新数据</button><button id="logout">退出登录</button></div></div>
<h1>运营概览</h1><p class="intro">网站访问与邮件订阅 · 数据实时读取，不保存订阅者个人邮箱</p>
<div id="status" class="status">正在读取数据…</div>
<div class="grid">
<div class="card"><div class="kicker">PAGE VIEWS · 30 DAYS</div><div class="value" id="pageviews">—</div><div class="hint">过去 30 天页面浏览量</div></div>
<div class="card"><div class="kicker">REFERRAL VIEWS · 30 DAYS</div><div class="value" id="referralViews">—</div><div class="hint">过去 30 天来自其他网站链接的页面浏览</div></div>
<div class="card"><div class="kicker">ACTIVE SUBSCRIBERS</div><div class="value" id="subscribers">—</div><div class="hint">当前有效订阅者</div></div>
<div class="card"><div class="kicker">NEW · 7 DAYS</div><div class="value" id="newSubscribers">—</div><div class="hint">过去 7 天新增有效订阅</div></div>
</div>
<section class="section"><h2>网站访问趋势</h2><div class="panel"><div id="chart" class="bars"></div><div class="hint">按 Cloudflare 日期维度汇总。访问数据来自 Cloudflare Web Analytics。</div></div></section>
<section class="section"><h2>邮件草稿</h2><div class="panel"><div class="grid" style="grid-template-columns:repeat(2,minmax(0,1fr));margin-bottom:12px">
<div><div class="kicker">DRAFTS</div><div class="value" id="draftCount">—</div><div class="hint">Buttondown 中尚未发送的草稿</div></div>
<div><div class="kicker">NEWSLETTER</div><div class="value" style="font-size:20px;margin-top:13px">Opera Lirico Weekly</div><div class="hint"><a href="https://buttondown.com/wl19971007" target="_blank" rel="noopener noreferrer">打开 Buttondown ↗</a></div></div>
</div><div id="drafts" class="drafts"><div class="empty">正在读取草稿…</div></div></div></section>
<p class="notice">安全说明：此后台只读取 Cloudflare 访问统计、Buttondown 订阅状态汇总和草稿标题；不会显示订阅者邮箱，不提供发送邮件操作。</p>
</main>
<script>
const $=id=>document.getElementById(id);
function showLogin(){ $("loginView").hidden=false; $("appView").hidden=true; }
function showApp(){ $("loginView").hidden=true; $("appView").hidden=false; }
function fmt(v){return Number(v||0).toLocaleString("zh-CN")}
$("loginForm").addEventListener("submit",async e=>{
 e.preventDefault();$("loginError").textContent="";
 try{const r=await fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({password:$("password").value})});
 if(!r.ok)throw new Error("密码不正确，或登录暂时受限。");$("password").value="";showApp();loadData();}
 catch(err){$("loginError").textContent=err.message;}
});
$("logout").addEventListener("click",async()=>{await fetch("/api/logout",{method:"POST"});showLogin();});
$("refresh").addEventListener("click",loadData);
function drawChart(days){
 const root=$("chart");root.replaceChildren();
 const max=Math.max(1,...days.map(x=>x.pageviews||0));
 days.forEach((d,i)=>{const w=document.createElement("div");w.className="bar-wrap";
 const b=document.createElement("div");b.className="bar";b.style.height=Math.max(2,(d.pageviews/max)*100)+"%";b.title=d.date+": "+fmt(d.pageviews);
 const l=document.createElement("div");l.className="bar-label";l.textContent=(i%5===0||i===days.length-1)?d.date.slice(5):"";
 w.append(b,l);root.append(w);});
}
function renderDrafts(items){
 const root=$("drafts");root.replaceChildren();
 if(!items.length){const p=document.createElement("div");p.className="empty";p.textContent="目前没有待审核草稿。";root.append(p);return;}
 items.forEach(item=>{const row=document.createElement("div");row.className="draft";
 const left=document.createElement("div");const title=document.createElement("strong");title.textContent=item.subject||"（无标题）";left.append(title);
 const small=document.createElement("small");small.textContent=item.created||"";left.append(small);row.append(left);
 root.append(row);});
}
async function loadData(){
 $("status").textContent="正在更新数据…";
 try{
  const r=await fetch("/api/data",{cache:"no-store"});if(r.status===401){showLogin();return;}if(!r.ok)throw new Error("数据读取失败");
  const d=await r.json();
  if(d.cloudflare&&d.cloudflare.ok){$("pageviews").textContent=fmt(d.cloudflare.pageviews);$("referralViews").textContent=fmt(d.cloudflare.referral_views);drawChart(d.cloudflare.days||[]);}
  else{$("pageviews").textContent="—";$("referralViews").textContent="—";}
  if(d.buttondown&&d.buttondown.ok){$("subscribers").textContent=fmt(d.buttondown.active_subscribers);$("newSubscribers").textContent=fmt(d.buttondown.new_subscribers_7d);$("draftCount").textContent=fmt(d.buttondown.draft_count);renderDrafts(d.buttondown.drafts||[]);}
  else{$("subscribers").textContent="—";$("newSubscribers").textContent="—";$("draftCount").textContent="—";$("drafts").textContent="Buttondown 数据暂时不可用。";}
  const issues=[];if(!d.cloudflare?.ok)issues.push("Cloudflare："+(d.cloudflare?.error||"不可用"));if(!d.buttondown?.ok)issues.push("Buttondown："+(d.buttondown?.error||"不可用"));
  $("status").textContent=(issues.length?issues.join("；"):"两项数据源均已连接")+" · 更新于 "+new Date(d.generated_at).toLocaleString("zh-CN");
 }catch(err){$("status").textContent=err.message;}
}
(async()=>{try{const r=await fetch("/api/session");if(r.ok){showApp();loadData();}else showLogin();}catch(e){showLogin();}})();
</script></body></html>`;

function response(body, status = 200, extra = {}) {
  return new Response(body, { status, headers: {
    "Content-Type": "text/html; charset=utf-8",
    "Cache-Control": "no-store, max-age=0",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
    ...extra
  }});
}
function json(data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data), { status, headers: {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store, max-age=0",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    ...extra
  }});
}
function constantTimeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  let diff = a.length ^ b.length;
  const n = Math.max(a.length, b.length);
  for (let i = 0; i < n; i++) diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return diff === 0;
}
function b64url(bytes) {
  let binary = "";
  new Uint8Array(bytes).forEach(x => binary += String.fromCharCode(x));
  return btoa(binary).replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}
async function signature(timestamp, secret) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return b64url(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode("opera-ops:" + timestamp)));
}
async function validSession(request, secret) {
  if (!secret || secret.length < 32) return false;
  const raw = request.headers.get("Cookie") || "";
  const found = raw.split(";").map(x => x.trim()).find(x => x.startsWith(SESSION_COOKIE + "="));
  if (!found) return false;
  let value;
  try { value = decodeURIComponent(found.slice(SESSION_COOKIE.length + 1)); } catch { return false; }
  const parts = value.split(".");
  if (parts.length !== 2 || !/^\d{13}$/.test(parts[0])) return false;
  const age = Date.now() - Number(parts[0]);
  if (age < 0 || age > SESSION_TTL_SECONDS * 1000) return false;
  return constantTimeEqual(parts[1], await signature(parts[0], secret));
}
function cookie(value, maxAge) {
  return SESSION_COOKIE + "=" + value + "; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=" + maxAge;
}
function sameOrigin(request) {
  const origin = request.headers.get("Origin");
  return !origin || origin === new URL(request.url).origin;
}
async function fetchJson(url, headers = {}) {
  const r = await fetch(url, { headers: { Accept: "application/json", ...headers }, signal: AbortSignal.timeout(20000) });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error("API returned HTTP " + r.status);
  return body;
}
async function getCloudflare(env) {
  const start = new Date(Date.now() - 29 * 86400000).toISOString().slice(0, 10);
  const end = new Date().toISOString().slice(0, 10);
  const q = 'query { viewer { accounts(filter: { accountTag: "' + env.CF_ACCOUNT_ID + '" }) { rumPageloadEventsAdaptiveGroups(limit: 1000, filter: { siteTag: "' + env.CF_WEB_ANALYTICS_SITE_TAG + '", date_geq: "' + start + '", date_leq: "' + end + '" }) { count sum { visits } dimensions { date requestHost } } } } }';
  const r = await fetch("https://api.cloudflare.com/client/v4/graphql", {
    method: "POST",
    headers: { Authorization: "Bearer " + env.CF_ANALYTICS_API_TOKEN, "Content-Type": "application/json" },
    body: JSON.stringify({ query: q }),
    signal: AbortSignal.timeout(20000)
  });
  const body = await r.json().catch(() => ({}));
  if (!r.ok || body.errors?.length) throw new Error("Cloudflare Analytics API query failed");
  const rows = body.data?.viewer?.accounts?.[0]?.rumPageloadEventsAdaptiveGroups;
  if (!Array.isArray(rows)) throw new Error("Cloudflare returned no analytics dataset");
  const map = new Map();
  for (const row of rows) {
    if (row.dimensions?.requestHost !== env.CF_WEB_ANALYTICS_HOST) continue;
    const date = row.dimensions?.date;
    if (!date) continue;
    const item = map.get(date) || { date, pageviews: 0, referral_views: 0 };
    item.pageviews += Number(row.count || 0);
    item.referral_views += Number(row.sum?.visits || 0);
    map.set(date, item);
  }
  const days = [];
  const cursor = new Date(start + "T12:00:00Z");
  const last = new Date(end + "T12:00:00Z");
  while (cursor <= last) {
    const date = cursor.toISOString().slice(0, 10);
    days.push(map.get(date) || { date, pageviews: 0, referral_views: 0 });
    cursor.setUTCDate(cursor.getUTCDate() + 1);
  }
  return { pageviews: days.reduce((s, x) => s + x.pageviews, 0), referral_views: days.reduce((s, x) => s + x.referral_views, 0), days };
}
async function getButtondown(env) {
  const headers = { Authorization: "Token " + env.BUTTONDOWN_API_KEY };
  let url = "https://api.buttondown.com/v1/subscribers";
  let active = 0, new7 = 0, pages = 0;
  const since = Date.now() - 7 * 86400000;
  while (url && pages++ < 100) {
    const parsed = new URL(url, "https://api.buttondown.com");
    if (parsed.protocol !== "https:" || parsed.hostname !== "api.buttondown.com") throw new Error("Unexpected Buttondown pagination URL");
    const page = await fetchJson(parsed.toString(), headers);
    for (const s of (page.results || [])) {
      const type = s.type || s.subscriber_type || "";
      const isActive = ["regular", "premium", "gifted", "trialed", "paused", "churning", "churned", "unpaid"].includes(type);
      if (isActive) {
        active++;
        const created = Date.parse(s.creation_date || "");
        if (Number.isFinite(created) && created >= since) new7++;
      }
    }
    url = page.next || null;
  }
  if (url) throw new Error("Buttondown subscriber pagination limit reached");
  let emailUrl = "https://api.buttondown.com/v1/emails?status=draft&excluded_fields=body";
  let draftCount = 0, emailPages = 0;
  const drafts = [];
  while (emailUrl && emailPages++ < 20) {
    const parsed = new URL(emailUrl, "https://api.buttondown.com");
    if (parsed.protocol !== "https:" || parsed.hostname !== "api.buttondown.com") throw new Error("Unexpected Buttondown pagination URL");
    const page = await fetchJson(parsed.toString(), headers);
    draftCount = Number(page.count ?? draftCount + (page.results || []).length);
    for (const item of (page.results || [])) {
      if (drafts.length >= 10) break;
      drafts.push({ subject: String(item.subject || "（无标题）").slice(0, 160), created: String(item.creation_date || "").slice(0, 10) });
    }
    emailUrl = page.next || null;
  }
  return { active_subscribers: active, new_subscribers_7d: new7, draft_count: draftCount, drafts };
}
async function getDashboardData(env) {
  const [cf, bd] = await Promise.allSettled([getCloudflare(env), getButtondown(env)]);
  return {
    generated_at: new Date().toISOString(),
    cloudflare: cf.status === "fulfilled" ? { ok: true, ...cf.value } : { ok: false, error: "读取失败，请检查 Cloudflare API Token、Account ID 和 Web Analytics 数据权限" },
    buttondown: bd.status === "fulfilled" ? { ok: true, ...bd.value } : { ok: false, error: "读取失败，请检查 Buttondown API Key" }
  };
}
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/" && request.method === "GET") return response(PAGE);
    if (url.pathname === "/api/login" && request.method === "POST") {
      if (!env.OPS_DASHBOARD_PASSWORD || env.OPS_DASHBOARD_PASSWORD.length < 32) return json({ error: "login_not_configured" }, 503);
      if (!sameOrigin(request)) return json({ error: "forbidden" }, 403);
      const ip = request.headers.get("CF-Connecting-IP") || "unknown";
      const now = Date.now();
      const attempt = loginAttempts.get(ip) || { count: 0, start: now };
      if (now - attempt.start > 10 * 60 * 1000) { attempt.count = 0; attempt.start = now; }
      if (attempt.count >= 8) return json({ error: "rate_limited" }, 429);
      let input = {};
      try { input = await request.json(); } catch {}
      if (!constantTimeEqual(String(input.password || ""), env.OPS_DASHBOARD_PASSWORD || "")) {
        attempt.count++; loginAttempts.set(ip, attempt);
        return json({ error: "unauthorized" }, 401);
      }
      loginAttempts.delete(ip);
      const timestamp = String(Date.now());
      const signed = timestamp + "." + await signature(timestamp, env.OPS_DASHBOARD_PASSWORD);
      return json({ ok: true }, 200, { "Set-Cookie": cookie(signed, SESSION_TTL_SECONDS) });
    }
    if (url.pathname === "/api/session" && request.method === "GET") {
      return await validSession(request, env.OPS_DASHBOARD_PASSWORD) ? json({ ok: true }) : json({ error: "unauthorized" }, 401);
    }
    if (url.pathname === "/api/logout" && request.method === "POST") {
      if (!sameOrigin(request)) return json({ error: "forbidden" }, 403);
      return json({ ok: true }, 200, { "Set-Cookie": cookie("", 0) });
    }
    if (url.pathname === "/api/data" && request.method === "GET") {
      if (!await validSession(request, env.OPS_DASHBOARD_PASSWORD)) return json({ error: "unauthorized" }, 401);
      if (!env.CF_ACCOUNT_ID || !env.CF_ANALYTICS_API_TOKEN || !env.BUTTONDOWN_API_KEY) return json({ error: "missing_configuration" }, 503);
      return json(await getDashboardData(env));
    }
    return json({ error: "not_found" }, 404);
  }
};