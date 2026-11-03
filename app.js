const $ = (selector) => document.querySelector(selector);
const sourceRoot = new URL('.', location.href);
let sourceData = [];
let installPrompt = null;

const opportunities = [
  {title:'78° Concorso Internazionale AsLiCo per Giovani Cantanti Lirici 2027',category:'青年歌手选拔 · 歌剧角色招募',place:'科莫 · 多地预选',deadline:'2026-11-25T18:00:00+01:00',summary:'为 2027/28 OperaLombardia 歌剧季选拔演员，也设青年歌手组。招募角色包括《拉美莫尔的露琪亚》《伊多美纽》等；报名费 70 欧元。',url:'https://aslico.org/edizione-in-corso/',source:'AsLiCo'},
  {title:'Concorso Internazionale di Canto lirico Francesco Morlacchi 2026',category:'国际声乐比赛',place:'佩鲁贾',deadline:'2026-11-30T23:59:00+01:00',summary:'比赛将于 2026 年 12 月 14–15 日举行，面向 18 至 35 岁歌手。报名费 80 欧元，需提交曲目、简历、身份证明及演唱视频。',url:'https://www.concorsomorlacchi.it/',source:'Morlacchi 声乐比赛'}
];

let repertoire = [];
let repertoireLoaded = false;function esc(text=''){return String(text).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));}
const languageNames={it:"意大利语",fr:"法语",en:"英语",de:"德语",es:"西班牙语",pt:"葡萄牙语",ru:"俄语"};
function languageLabel(code="it"){const key=String(code).toLowerCase().split("-")[0];return languageNames[key]||"原文语言";}
function googleReadUrl(item){
  if((item.text||"").length>5000)return "";
  const language=String(item.language||"auto").toLowerCase().split("-")[0];
  const url=new URL("https://translate.google.com/");
  url.searchParams.set("sl",language);
  url.searchParams.set("tl","zh-CN");
  url.searchParams.set("hl","zh-CN");
  url.searchParams.set("text",item.text||"");
  url.searchParams.set("op","translate");
  return url.toString();
}
async function loadRepertoire(){
 try{
   const response=await fetch(new URL('data/repertoire.json',sourceRoot),{cache:'no-store'});
   if(!response.ok)throw new Error('HTTP '+response.status);
   const data=await response.json();
   repertoire=data.items||[];
   repertoireLoaded=true;
   renderMusicSearch($('#musicSearchInput').value);
 }catch(error){
   repertoireLoaded=false;
   $('#musicSearchResults').innerHTML='<div class="music-empty">曲目库暂时无法更新，请稍后重试。</div>';
 }
}
function renderMusicSearch(rawQuery){
 const target=$('#musicSearchResults');
 const query=rawQuery.trim();
 if(!query){
   target.innerHTML='<div class="music-empty">输入歌名即可查看站内歌词原文。曲目库每天尝试从公开文本目录补充，未必涵盖你搜索的作品。</div>';
   return;
 }
 if(!repertoireLoaded){
   target.innerHTML='<div class="music-empty">曲目库正在更新，请稍候。</div>';
   return;
 }
 const terms=query.toLocaleLowerCase().split(/[\\/,，、;；|]+/).map(x=>x.trim()).filter(Boolean);
 const matches=repertoire.filter(item=>{
   const haystack=[item.title,...(item.aliases||[]),item.composer,item.work,item.kind,item.text].filter(Boolean).join(' ').toLocaleLowerCase();
   return terms.some(term=>haystack.includes(term));
 });
 if(!matches.length){
   target.innerHTML='<div class="music-empty"><strong>这首作品目前还没有收录。</strong><p>不会跳到其他网站。曲目库每天尝试从公开文本目录补充作品；这并不代表系统已单独搜索这首歌，收录后可直接在本站搜索。</p></div>';
   return;
 }
 target.innerHTML=matches.map(item=>`<article class="music-result">
   <div class="music-result-top"><span class="music-kind">${esc(item.kind)}</span><span class="music-voice">${esc(item.voice)}</span></div>
   <h3>${esc(item.title)}</h3>
   <p class="music-byline">${esc(item.composer)} · ${esc(item.work)}</p>
   <div class="music-text"><div class="music-text-label">歌词原文 · ${esc(languageLabel(item.language))}</div><p class="lyrics">${esc(item.text).replace(/\n/g,'<br>')}</p></div>
   <div class="music-reading"><div><span class="music-text-label">泛读 · ${esc(languageLabel(item.language))}</span><p>在 Google 翻译中打开后，点击“听取原文”；会按这首作品的原文语言朗读。</p></div>${googleReadUrl(item)?'<a class="reading-link" href="'+esc(googleReadUrl(item))+'" target="_blank" rel="noopener noreferrer">Google 翻译朗读原文 ↗</a>':'<span class="score-unavailable">文本超过 Google 翻译单次朗读长度</span>'}</div>
   <p class="music-meaning"><strong>大意：</strong>${esc(item.summary)}</p>
   <div class="music-score"><div><span class="music-text-label">乐谱</span><p>${item.downloadUrl?'本站提供已核验的可下载版本。':'本站暂未托管乐谱 PDF。可以先查看 IMSLP 对应作品页；版本与地区版权请自行核对。'}</p></div>${item.downloadUrl?'<a class="score-download" href="'+esc(item.downloadUrl)+'" download>下载乐谱 PDF ↓</a>':item.scoreUrl?'<a class="score-imslp" href="'+esc(item.scoreUrl)+'" target="_blank" rel="noopener noreferrer">IMSLP 查看乐谱 ↗</a>':'<span class="score-unavailable">暂无乐谱链接</span>'}</div>
   <div class="music-source"><span>文本出处：${esc(item.textSourceName||'公开文本来源')} · 本文已收录在本站，搜索和阅读无需跳转。</span></div>
 </article>`).join('');
}
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
$('#musicSearchForm').addEventListener('submit',event=>{event.preventDefault();renderMusicSearch($('#musicSearchInput').value);});
$('#musicSearchInput').addEventListener('input',event=>renderMusicSearch(event.target.value));
document.querySelectorAll('.search-chip').forEach(button=>button.addEventListener('click',()=>{const q=button.dataset.query;$('#musicSearchInput').value=q;renderMusicSearch(q);}));
renderMusicSearch('');
loadRepertoire();
loadData();
