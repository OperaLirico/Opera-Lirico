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
.socialQueue{display:grid;gap:16px}.socialCard{display:grid;grid-template-columns:minmax(180px,260px) minmax(0,1fr);gap:18px;padding:16px 0;border-bottom:1px solid var(--line)}.socialCard:last-child{border:0}
.socialImage{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:10px;background:#f5f0e5}.socialEditor{min-width:0}.socialEditor textarea{width:100%;min-height:210px;padding:12px;border:1px solid var(--line);border-radius:10px;font:14px/1.7 system-ui,sans-serif;resize:vertical;background:#fff}
.socialActions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}.socialMeta{font-size:12px;color:var(--muted);margin:4px 0 10px}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 9px;font-size:11px;color:var(--green)}
.masterclassQueue{display:grid;gap:14px}.masterclassCard{border:1px solid var(--line);border-radius:12px;padding:16px;background:#fffefa}.masterclassCard h3{font:600 19px Georgia,serif;margin:0 0 6px}.masterclassMeta{font-size:12px;color:var(--muted);margin:5px 0}.masterclassExcerpt{font-size:13px;line-height:1.65;background:#f6f3eb;padding:12px;border-radius:8px;margin:10px 0;overflow-wrap:anywhere}.masterclassNotes{width:100%;min-height:72px;padding:10px;border:1px solid var(--line);border-radius:8px;font:14px/1.6 system-ui,sans-serif;margin-top:10px}.masterclassActions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.masterclassState{font-size:12px;color:var(--green);margin-top:8px}
.workflowList{display:grid;gap:0}.workflowRow{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:center;padding:11px 0;border-bottom:1px solid var(--line)}.workflowRow:last-child{border:0}.workflowName{font-weight:600}.workflowMeta{font-size:11px;color:var(--muted)}.workflowBadge{font-size:11px;border:1px solid var(--line);border-radius:999px;padding:3px 9px;white-space:nowrap}.workflowBadge.success{color:#236347}.workflowBadge.failure{color:#a13c32}.workflowBadge.running{color:#8a652d}.workflowBadge.neutral{color:var(--muted)}
@media(max-width:620px){.socialCard{grid-template-columns:1fr}.socialImage{max-width:320px}.socialEditor textarea{min-height:180px}}
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
<section class="section" style="margin-top:0"><h2>自动化运行状态</h2><div class="panel"><p class="hint">最近 20 次 GitHub Actions 运行 · 失败会自动记录并提醒</p><div id="workflowRuns" class="workflowList"><div class="empty">正在读取运行记录…</div></div></div></section>
<div class="grid">
<div class="card"><div class="kicker">PAGE VIEWS · 30 DAYS</div><div class="value" id="pageviews">—</div><div class="hint">过去 30 天页面浏览量</div></div>
<div class="card"><div class="kicker">VISITS · 30 DAYS</div><div class="value" id="visits">—</div><div class="hint">过去 30 天访问次数（Visits）</div></div>
<div class="card"><div class="kicker">ACTIVE SUBSCRIBERS</div><div class="value" id="subscribers">—</div><div class="hint">当前有效订阅者</div></div>
<div class="card"><div class="kicker">NEW · 7 DAYS</div><div class="value" id="newSubscribers">—</div><div class="hint">过去 7 天新增有效订阅</div></div>
</div>
<section class="section"><h2>网站访问趋势</h2><div class="panel"><div id="chart" class="bars"></div><div class="hint">按 Cloudflare 日期维度汇总。访问数据来自 Cloudflare Web Analytics。</div></div></section>
<section class="section"><h2>邮件草稿</h2><div class="panel"><div class="grid" style="grid-template-columns:repeat(2,minmax(0,1fr));margin-bottom:12px">
<div><div class="kicker">DRAFTS</div><div class="value" id="draftCount">—</div><div class="hint">Buttondown 中尚未发送的草稿</div></div>
<div><div class="kicker">NEWSLETTER</div><div class="value" style="font-size:20px;margin-top:13px">Opera Lirico Weekly</div><div class="hint"><a href="https://buttondown.com/wl19971007" target="_blank" rel="noopener noreferrer">打开 Buttondown ↗</a></div></div>
</div><div id="drafts" class="drafts"><div class="empty">正在读取草稿…</div></div></div></section>
<section class="section"><h2>社交媒体内容审核</h2><div class="panel">
<p class="hint">自动生成的中文图片与文案会先进入这里。保存修改或审核通过都不会自动发布到社交平台。</p>
<div id="contentQueue" class="socialQueue"><div class="empty">正在读取内容草稿…</div></div>
</div></section>
<section class="section"><h2>大师班候选审核</h2><div class="panel">
<p class="hint">每日自动发现的课程线索。请打开主办方原始页面核对日期、费用、报名条件和截止时间。核实通过只代表审核完成，不会自动发布到网站。</p>
<div id="masterclassQueue" class="masterclassQueue"><div class="empty">正在读取大师班候选…</div></div>
</div></section>
<p class="notice">安全说明：访问统计、订阅汇总和社交媒体草稿均受后台登录保护；此后台不提供自动发布或邮件发送操作。</p>
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
function renderWorkflowRuns(items){
 const root=$("workflowRuns");root.replaceChildren();
 if(!items.length){const p=document.createElement("div");p.className="empty";p.textContent="暂时没有可显示的运行记录。";root.append(p);return;}
 items.forEach(item=>{
  const row=document.createElement("div");row.className="workflowRow";
  const left=document.createElement("div");
  const name=document.createElement("div");name.className="workflowName";name.textContent=item.name||"未命名工作流";left.append(name);
  const meta=document.createElement("div");meta.className="workflowMeta";meta.textContent=[item.event,item.branch,item.created_at?new Date(item.created_at).toLocaleString("zh-CN"):""].filter(Boolean).join(" · ");left.append(meta);
  const status=document.createElement("span");status.className="workflowBadge "+(item.conclusion==="success"?"success":item.conclusion==="failure"?"failure":item.status==="in_progress"?"running":"neutral");
  status.textContent=item.conclusion==="success"?"成功":item.conclusion==="failure"?"失败":item.conclusion==="cancelled"?"已取消":item.status==="in_progress"?"运行中":"排队中";
  const link=document.createElement("a");
  try{const u=new URL(item.html_url);if(u.hostname==="github.com"&&u.pathname.startsWith("/OperaLirico/Opera-Lirico/actions/runs/")){link.href=u.href;link.target="_blank";link.rel="noopener noreferrer";link.textContent="查看 ↗";}else link.textContent="";}catch{link.textContent="";}
  const right=document.createElement("div");right.style.display="flex";right.style.alignItems="center";right.style.gap="8px";right.append(status);if(link.href)right.append(link);
  row.append(left,right);root.append(row);
 });
}
async function loadWorkflowRuns(){
 const root=$("workflowRuns");root.textContent="正在读取运行记录…";
 try{const r=await fetch("/api/workflows",{cache:"no-store"});if(r.status===401){showLogin();return;}if(!r.ok)throw new Error("运行记录读取失败");const d=await r.json();renderWorkflowRuns(d.runs||[]);}
 catch(err){root.textContent="自动化运行记录暂时不可用，请稍后刷新。";}
}
async function loadContentQueue(){
 const root=$("contentQueue");root.textContent="正在读取内容草稿…";
 try{
  const r=await fetch("/api/content/drafts",{cache:"no-store"});
  if(r.status===401){showLogin();return;}
  if(!r.ok)throw new Error("内容草稿读取失败");
  const d=await r.json();root.replaceChildren();
  if(!d.items||!d.items.length){const p=document.createElement("div");p.className="empty";p.textContent="目前没有待审核内容。";root.append(p);return;}
  d.items.forEach(item=>{
   const card=document.createElement("article");card.className="socialCard";
   const image=document.createElement("img");image.className="socialImage";image.alt=item.title||"社交媒体图片";image.src="data:image/png;base64,"+item.image_base64;
   const editor=document.createElement("div");editor.className="socialEditor";
   const heading=document.createElement("strong");heading.textContent=item.title||"未命名内容";editor.append(heading);
   const meta=document.createElement("div");meta.className="socialMeta";meta.textContent=(item.category||"音乐机会")+" · "+({approved:"已审核，待手动发布",needs_changes:"需要修改",published:"已发布",pending_review:"待审核"}[item.status]||"待审核");editor.append(meta);
   const link=document.createElement("a");link.href=item.source_url;link.target="_blank";link.rel="noopener noreferrer";link.textContent="打开官方来源 ↗";editor.append(link);
   const area=document.createElement("textarea");area.value=item.caption||"";area.setAttribute("aria-label","社交媒体文案");editor.append(area);
   const actions=document.createElement("div");actions.className="socialActions";
   const save=document.createElement("button");save.textContent="保存文案";save.addEventListener("click",()=>updateDraft(item.id,{caption:area.value,status:"pending_review"},save));
   const approve=document.createElement("button");approve.className="primary";approve.textContent="审核通过";approve.addEventListener("click",()=>updateDraft(item.id,{caption:area.value,status:"approved"},approve));
   const revise=document.createElement("button");revise.textContent="需要修改";revise.addEventListener("click",()=>updateDraft(item.id,{caption:area.value,status:"needs_changes"},revise));
   const published=document.createElement("button");published.textContent="标记已发布";published.addEventListener("click",()=>updateDraft(item.id,{caption:area.value,status:"published"},published));
   actions.append(save,approve,revise,published);editor.append(actions);card.append(image,editor);root.append(card);
  });
 }catch(err){root.textContent=err.message;}
}
async function updateDraft(id,payload,button){
 const old=button.textContent;button.disabled=true;button.textContent="保存中…";
 try{const r=await fetch("/api/content/drafts/"+encodeURIComponent(id),{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
 if(!r.ok)throw new Error("保存失败，请刷新后重试");await loadContentQueue();
 }catch(err){button.textContent=err.message;button.disabled=false;return;}button.textContent=old;button.disabled=false;
}
async function loadMasterclassQueue(){
 const root=$("masterclassQueue");root.textContent="正在读取大师班候选…";
 try{
  const r=await fetch("/api/masterclasses/candidates",{cache:"no-store"});
  if(r.status===401){showLogin();return;}
  if(!r.ok)throw new Error("大师班候选读取失败");
  const d=await r.json();root.replaceChildren();
  const items=d.items||[];
  if(!items.length){const p=document.createElement("div");p.className="empty";p.textContent="目前没有待审核候选。";root.append(p);return;}
  items.forEach(item=>{
   const card=document.createElement("article");card.className="masterclassCard";
   const heading=document.createElement("h3");heading.textContent=item.title_hint||"未命名课程";card.append(heading);
   const meta=document.createElement("div");meta.className="masterclassMeta";
   const state=item.review?.status||"pending_manual_review";
   const stateLabel={pending_manual_review:"待人工审核",verified_pending_publication:"已核实 · 待整理发布",needs_more_info:"需要补充信息",rejected:"已排除"}[state]||state;
   meta.textContent=(item.source_name||"未知来源")+" · "+(item.publisher_status==="official"?"主办方来源":"第三方发现来源")+" · "+stateLabel;
   card.append(meta);
   const dates=document.createElement("div");dates.className="masterclassMeta";dates.textContent="发现日期线索："+(item.date_signals||[]).join("、");card.append(dates);
   const checked=document.createElement("div");checked.className="masterclassMeta";checked.textContent="最近抓取："+(item.checked_at||"—")+" · 首次发现："+(item.first_seen_at||"—");card.append(checked);
   const source=document.createElement("a");source.href=item.source_url||"#";source.target="_blank";source.rel="noopener noreferrer";source.textContent="打开候选原始来源 ↗";card.append(source);
   const discovered=document.createElement("div");discovered.className="masterclassMeta";discovered.textContent="发现入口："+(item.discovered_from||"—");card.append(discovered);
   const excerpt=document.createElement("div");excerpt.className="masterclassExcerpt";excerpt.textContent=item.evidence_excerpt||"抓取结果未提供摘录。";card.append(excerpt);
   const notes=document.createElement("textarea");notes.className="masterclassNotes";notes.placeholder="记录核实结果：准确日期、报名截止、费用、年龄限制、官方申请链接等…";notes.value=item.review?.notes||item.review_notes||"";notes.setAttribute("aria-label","大师班审核备注");card.append(notes);
   const status=document.createElement("div");status.className="masterclassState";status.textContent=item.review?.reviewed_at?"上次审核："+new Date(item.review.reviewed_at).toLocaleString("zh-CN"):"尚未审核";card.append(status);
   const actions=document.createElement("div");actions.className="masterclassActions";
   const verified=document.createElement("button");verified.className="primary";verified.textContent="核实通过（待发布）";verified.disabled=item.publisher_status!=="official";
   verified.title=verified.disabled?"第三方目录只能作为线索，需先找到主办方官方页面。":"核实通过不会自动发布。";
   verified.addEventListener("click",()=>saveMasterclassReview(item.candidate_id,"verified_pending_publication",notes.value,verified));
   const more=document.createElement("button");more.textContent="需要补充信息";more.addEventListener("click",()=>saveMasterclassReview(item.candidate_id,"needs_more_info",notes.value,more));
   const reject=document.createElement("button");reject.textContent="排除";reject.addEventListener("click",()=>saveMasterclassReview(item.candidate_id,"rejected",notes.value,reject));
   actions.append(verified,more,reject);card.append(actions);root.append(card);
  });
 }catch(err){root.textContent=err.message;}
}
async function saveMasterclassReview(id,state,notes,button){
 const old=button.textContent;button.disabled=true;button.textContent="保存中…";
 try{
  const r=await fetch("/api/masterclasses/candidates/"+encodeURIComponent(id),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({status:state,notes})});
  if(!r.ok){const d=await r.json().catch(()=>({}));throw new Error(d.error==="official_source_required"?"请先找到并核对主办方官方页面。":"审核结果保存失败，请刷新后重试。");}
  await loadMasterclassQueue();
 }catch(err){button.textContent=err.message;button.disabled=false;return;}
 button.textContent=old;button.disabled=false;
}
async function loadData(){
 $("status").textContent="正在更新数据…";
 try{
  const r=await fetch("/api/data",{cache:"no-store"});if(r.status===401){showLogin();return;}if(!r.ok)throw new Error("数据读取失败");
  const d=await r.json();
  if(d.cloudflare&&d.cloudflare.ok){$("pageviews").textContent=fmt(d.cloudflare.pageviews);$("visits").textContent=fmt(d.cloudflare.visits);drawChart(d.cloudflare.days||[]);}
  else{$("pageviews").textContent="—";$("visits").textContent="—";}
  if(d.buttondown&&d.buttondown.ok){$("subscribers").textContent=fmt(d.buttondown.active_subscribers);$("newSubscribers").textContent=fmt(d.buttondown.new_subscribers_7d);$("draftCount").textContent=fmt(d.buttondown.draft_count);renderDrafts(d.buttondown.drafts||[]);}
  else{$("subscribers").textContent="—";$("newSubscribers").textContent="—";$("draftCount").textContent="—";$("drafts").textContent="Buttondown 数据暂时不可用。";}
  const issues=[];if(!d.cloudflare?.ok)issues.push("Cloudflare："+(d.cloudflare?.error||"不可用"));if(!d.buttondown?.ok)issues.push("Buttondown："+(d.buttondown?.error||"不可用"));
  loadContentQueue();
  loadMasterclassQueue();
  loadWorkflowRuns();
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
    "Content-Security-Policy": "default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
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
    // The siteTag filter above already scopes this query to this Web Analytics site.
    // Do not discard rows based on requestHost: Cloudflare may normalize or omit that dimension.
    const date = row.dimensions?.date;
    if (!date) continue;
    const item = map.get(date) || { date, pageviews: 0, visits: 0 };
    item.pageviews += Number(row.count || 0);
    item.visits += Number(row.sum?.visits || 0);
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
  return { pageviews: days.reduce((s, x) => s + x.pageviews, 0), visits: days.reduce((s, x) => s + x.visits, 0), days };
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
      const isActive = ["regular", "premium", "gifted", "trialed", "churning", "churned", "paused", "past_due"].includes(type);
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
    if (url.pathname === "/api/content/drafts" && request.method === "GET") {
      if (!await validSession(request, env.OPS_DASHBOARD_PASSWORD)) return json({ error: "unauthorized" }, 401);
      if (!env.CONTENT_DRAFTS) return json({ error: "content_storage_not_configured" }, 503);
      const listed = await env.CONTENT_DRAFTS.list({ prefix: "draft:", limit: 50 });
      const items = await Promise.all(listed.keys.map(async key => {
        const value = await env.CONTENT_DRAFTS.get(key.name, "json");
        return value && typeof value === "object" ? value : null;
      }));
      return json({ items: items.filter(Boolean).sort((a,b) => String(b.created_at||"").localeCompare(String(a.created_at||""))) });
    }
    if (url.pathname === "/api/content/drafts" && request.method === "POST") {
      if (!await validSession(request, env.OPS_DASHBOARD_PASSWORD)) return json({ error: "unauthorized" }, 401);
      if (!sameOrigin(request)) return json({ error: "forbidden" }, 403);
      if (!env.CONTENT_DRAFTS) return json({ error: "content_storage_not_configured" }, 503);
      const raw = await request.text();
      if (raw.length > 1800000) return json({ error: "payload_too_large" }, 413);
      let item = {}; try { item = JSON.parse(raw); } catch { return json({ error: "invalid_json" }, 400); }
      const id = String(item.id || "");
      const source = String(item.source_url || "");
      if (!/^[a-zA-Z0-9_-]{1,100}$/.test(id) || !String(item.title||"").trim() || !/^https:\/\//i.test(source) || !/^[A-Za-z0-9+/]+=*$/.test(String(item.image_base64||"")) || String(item.image_base64).length > 1400000) {
        return json({ error: "invalid_draft" }, 400);
      }
      const key = "draft:"+id;
      const existing = await env.CONTENT_DRAFTS.get(key, "json");
      if (existing) return json({ ok: true, skipped: true, id, status: existing.status });
      const record = {
        id, title: String(item.title).slice(0,240), category: String(item.category||"音乐机会").slice(0,80),
        caption: String(item.caption||"").slice(0,12000), source_url: source.slice(0,2000),
        image_base64: String(item.image_base64), status: "pending_review",
        created_at: new Date().toISOString(), updated_at: new Date().toISOString()
      };
      await env.CONTENT_DRAFTS.put(key, JSON.stringify(record), { expirationTtl: 60*60*24*30 });
      return json({ ok: true, id, status: record.status }, 201);
    }
    if (url.pathname.startsWith("/api/content/drafts/") && request.method === "PATCH") {
      if (!await validSession(request, env.OPS_DASHBOARD_PASSWORD)) return json({ error: "unauthorized" }, 401);
      if (!sameOrigin(request)) return json({ error: "forbidden" }, 403);
      if (!env.CONTENT_DRAFTS) return json({ error: "content_storage_not_configured" }, 503);
      const id = decodeURIComponent(url.pathname.slice("/api/content/drafts/".length));
      if (!/^[a-zA-Z0-9_-]{1,100}$/.test(id)) return json({ error: "invalid_id" }, 400);
      const record = await env.CONTENT_DRAFTS.get("draft:"+id, "json");
      if (!record) return json({ error: "not_found" }, 404);
      let input = {}; try { input = await request.json(); } catch { return json({ error: "invalid_json" }, 400); }
      if (input.status && !["pending_review","approved","needs_changes","published"].includes(input.status)) return json({ error: "invalid_status" }, 400);
      if (input.caption !== undefined) record.caption = String(input.caption).slice(0,12000);
      if (input.status) record.status = input.status;
      record.updated_at = new Date().toISOString();
      await env.CONTENT_DRAFTS.put("draft:"+id, JSON.stringify(record), { expirationTtl: 60*60*24*30 });
      return json({ ok: true, id, status: record.status });
    }
    if (url.pathname === "/api/masterclasses/candidates" && request.method === "GET") {
      if (!await validSession(request, env.OPS_DASHBOARD_PASSWORD)) return json({ error: "unauthorized" }, 401);
      if (!env.CONTENT_DRAFTS) return json({ error: "content_storage_not_configured" }, 503);
      try {
        const source = await fetchJson("https://raw.githubusercontent.com/OperaLirico/Opera-Lirico/main/data/masterclass_candidates.json");
        const items = Array.isArray(source.items) ? source.items.slice(0, 300) : [];
        const reviews = await Promise.all(items.map(async item => {
          const ids = [item.candidate_id, ...(Array.isArray(item.legacy_candidate_ids) ? item.legacy_candidate_ids : [])];
          for (const id of ids) {
            const review = await env.CONTENT_DRAFTS.get("masterclass-review:" + id, "json");
            if (review) return review;
          }
          return null;
        }));
        return json({
          updated_at: source.updated_at || null,
          candidate_count: items.length,
          items: items.map((item, index) => ({ ...item, review: reviews[index] || null }))
        });
      } catch (error) {
        return json({ error: "candidate_source_unavailable", message: "无法读取 GitHub 候选队列，请稍后重试。" }, 502);
      }
    }
    if (url.pathname.startsWith("/api/masterclasses/candidates/") && request.method === "POST") {
      if (!await validSession(request, env.OPS_DASHBOARD_PASSWORD)) return json({ error: "unauthorized" }, 401);
      if (!sameOrigin(request)) return json({ error: "forbidden" }, 403);
      if (!env.CONTENT_DRAFTS) return json({ error: "content_storage_not_configured" }, 503);
      const id = decodeURIComponent(url.pathname.slice("/api/masterclasses/candidates/".length));
      if (!/^[a-f0-9]{12}$/i.test(id)) return json({ error: "invalid_candidate_id" }, 400);
      const raw = await request.text();
      if (raw.length > 8000) return json({ error: "payload_too_large" }, 413);
      let input = {};
      try { input = JSON.parse(raw); } catch { return json({ error: "invalid_json" }, 400); }
      const allowed = ["verified_pending_publication", "needs_more_info", "rejected"];
      if (!allowed.includes(input.status)) return json({ error: "invalid_status" }, 400);
      let candidate;
      try {
        const source = await fetchJson("https://raw.githubusercontent.com/OperaLirico/Opera-Lirico/main/data/masterclass_candidates.json");
        candidate = (source.items || []).find(item => item.candidate_id === id);
      } catch {
        return json({ error: "candidate_source_unavailable" }, 502);
      }
      if (!candidate) return json({ error: "candidate_not_found" }, 404);
      if (input.status === "verified_pending_publication" && candidate.publisher_status !== "official") {
        return json({ error: "official_source_required" }, 400);
      }
      const record = {
        candidate_id: id,
        status: input.status,
        notes: String(input.notes || "").slice(0, 3000),
        reviewed_at: new Date().toISOString(),
        title_hint: String(candidate.title_hint || "").slice(0, 240),
        source_name: String(candidate.source_name || "").slice(0, 160),
        source_url: String(candidate.source_url || "").slice(0, 2000),
        publisher_status: String(candidate.publisher_status || "unknown")
      };
      await env.CONTENT_DRAFTS.put("masterclass-review:" + id, JSON.stringify(record), { expirationTtl: 60 * 60 * 24 * 365 });
      return json({ ok: true, review: record });
    }
    if (url.pathname === "/api/workflows" && request.method === "GET") {
      if (!await validSession(request, env.OPS_DASHBOARD_PASSWORD)) return json({ error: "unauthorized" }, 401);
      try {
        const source = await fetchJson("https://api.github.com/repos/OperaLirico/Opera-Lirico/actions/runs?per_page=20", {
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "Opera-Lirico-Operations-Dashboard"
        });
        const runs = (Array.isArray(source.workflow_runs) ? source.workflow_runs : []).slice(0, 20).map(run => ({
          id: run.id,
          name: String(run.name || "").slice(0, 160),
          event: String(run.event || ""),
          status: String(run.status || ""),
          conclusion: run.conclusion || null,
          branch: String(run.head_branch || "").slice(0, 120),
          created_at: run.created_at || null,
          html_url: run.html_url || ""
        }));
        return json({ updated_at: new Date().toISOString(), runs });
      } catch {
        return json({ error: "workflow_runs_unavailable" }, 502);
      }
    }
    if (url.pathname === "/api/data" && request.method === "GET") {
      if (!await validSession(request, env.OPS_DASHBOARD_PASSWORD)) return json({ error: "unauthorized" }, 401);
      if (!env.CF_ACCOUNT_ID || !env.CF_ANALYTICS_API_TOKEN || !env.BUTTONDOWN_API_KEY) return json({ error: "missing_configuration" }, 503);
      return json(await getDashboardData(env));
    }
    return json({ error: "not_found" }, 404);
  }
};