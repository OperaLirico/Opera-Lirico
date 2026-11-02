const $ = (selector) => document.querySelector(selector);
const sourceRoot = new URL('.', location.href);
let sourceData = [];
let installPrompt = null;

const opportunities = [
  {title:'78° Concorso Internazionale AsLiCo per Giovani Cantanti Lirici 2027',category:'青年歌手选拔 · 歌剧角色招募',place:'科莫 · 多地预选',deadline:'2026-11-25T18:00:00+01:00',summary:'为 2027/28 OperaLombardia 歌剧季选拔演员，也设青年歌手组。招募角色包括《拉美莫尔的露琪亚》《伊多美纽》等；报名费 70 欧元。',url:'https://aslico.org/edizione-in-corso/',source:'AsLiCo'},
  {title:'Concorso Internazionale di Canto lirico Francesco Morlacchi 2026',category:'国际声乐比赛',place:'佩鲁贾',deadline:'2026-11-30T23:59:00+01:00',summary:'比赛将于 2026 年 12 月 14–15 日举行，面向 18 至 35 岁歌手。报名费 80 欧元，需提交曲目、简历、身份证明及演唱视频。',url:'https://www.concorsomorlacchi.it/',source:'Morlacchi 声乐比赛'}
];

function esc(text=''){return String(text).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));}
function formatDate(iso){return new Intl.DateTimeFormat('zh-CN',{timeZone:'Europe/Rome',month:'long',day:'numeric',hour:'2-digit',minute:'2-digit'}).format(new Date(iso));}
function renderOpportunities(){
 const now=Date.now();
 const current=opportunities.filter(o=>new Date(o.deadline).getTime()>=now);
 $('#opportunityCount').textContent=current.length;
 $('#opportunities').innerHTML=current.length?current.map(o=>`<article class="opportunity-card"><div class="card-top"><span class="badge">${esc(o.category)}</span><span class="deadline">截止 ${formatDate(o.deadline)}</span></div><h3>${esc(o.title)}</h3><p>${esc(o.summary)}</p><div class="card-meta"><span>⌖ ${esc(o.place)}</span><span>主办方：${esc(o.source)}</span></div><a class="card-link" href="${esc(o.url)}" target="_blank" rel="noopener">查看主办方公告 <span>↗</span></a></article>`).join(''):'<div class="empty">目前没有已确认仍在报名的项目。你可以看看下方各机构的最新动态。</div>';
}
function renderSources(){
 const q=$('#searchInput').value.trim().toLocaleLowerCase();
 const status=$('#statusFilter').value;
 const filtered=sourceData.filter(s=>(status==='all'||(status==='ok'?s.status==='ok':s.status!=='ok'))&&(!q||`${s.source} ${s.title} ${(s.relevant_lines||[]).join(' ')}`.toLocaleLowerCase().includes(q)));
 $('#sourceCount').textContent=`${filtered.length}/${sourceData.length}`;
 $('#sources').innerHTML=filtered.length?filtered.map(s=>{
   const lines=(s.relevant_lines||[]).filter(x=>!x.includes('Privacy')&&!x.includes('cookie')).slice(0,4);
   const stamp=s.checked_at?new Intl.DateTimeFormat('zh-CN',{timeZone:'Europe/Rome',dateStyle:'medium',timeStyle:'short'}).format(new Date(s.checked_at)):'—';
   return `<article class="source-card"><div class="source-title"><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.source)}</a><span class="status ${s.status==='ok'?'':'error'}">${s.status==='ok'?'页面可访问':`暂时无法读取 ${esc(s.http_status||'')}`}</span></div><p class="source-snippet"><strong>${esc(s.title||'暂未读取到页面标题')}</strong>${lines.length?'<br>'+lines.map(esc).join(' · '):'<br>这次没有找到可展示的招募或比赛相关内容。'}</p><div class="source-foot"><span>最近查看：${stamp}</span><span>${s.status==='ok'?'自动摘录网页内容；请打开公告核对详情':'本次读取失败；可直接打开官网查看'}</span></div></article>`;
 }).join(''):'<div class="empty">没有找到符合条件的来源。</div>';
}
async function loadData(){
 $('#updatedAt').textContent='正在更新来源动态…';
 try{
   const res=await fetch(new URL('data/sources.json',sourceRoot),{cache:'no-store'});
   if(!res.ok)throw new Error(`HTTP ${res.status}`);
   const data=await res.json();sourceData=data.sources||data;
   const checked=data.generated_at||sourceData[0]?.checked_at;
   $('#updatedAt').textContent=checked?`最近查看：${new Intl.DateTimeFormat('zh-CN',{timeZone:'Europe/Rome',dateStyle:'medium',timeStyle:'short'}).format(new Date(checked))}`:'来源动态已更新';
   renderSources();
 }catch(error){
   $('#updatedAt').textContent='暂时无法更新来源动态';
   $('#sources').innerHTML=`<div class="empty">暂时无法读取数据（${esc(error.message)}）。请过一会儿再试。</div>`;
 }
 renderOpportunities();
}
$('#searchInput').addEventListener('input',renderSources);
$('#statusFilter').addEventListener('change',renderSources);
$('#refreshButton').addEventListener('click',loadData);
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();installPrompt=event;$('#installButton').hidden=false;});
$('#installButton').addEventListener('click',async()=>{if(installPrompt){installPrompt.prompt();await installPrompt.userChoice;installPrompt=null;$('#installButton').hidden=true;}else{alert('iPhone 用户可在 Safari 中点“分享”，再选“添加到主屏幕”。');}});
if(/iphone|ipad|ipod/i.test(navigator.userAgent)&&!window.navigator.standalone){$('#installButton').hidden=false;}
if('serviceWorker' in navigator && /^https?:$/.test(location.protocol))navigator.serviceWorker.register(new URL('service-worker.js',sourceRoot)).catch(()=>{});
loadData();
