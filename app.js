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
const languageNames={it:"意大利语",fr:"法语",en:"英语",de:"德语",es:"西班牙语",pt:"葡萄牙语",ru:"俄语",da:"丹麦语",sv:"瑞典语",no:"挪威语",nl:"荷兰语",pl:"波兰语",cs:"捷克语",hu:"匈牙利语",fi:"芬兰语",el:"希腊语",la:"拉丁语",is:"冰岛语",cy:"威尔士语",ga:"爱尔兰语",sco:"苏格兰语",gd:"苏格兰盖尔语",ca:"加泰罗尼亚语",ro:"罗马尼亚语",hr:"克罗地亚语",sr:"塞尔维亚语",bg:"保加利亚语",uk:"乌克兰语",sl:"斯洛文尼亚语",sk:"斯洛伐克语",et:"爱沙尼亚语",lv:"拉脱维亚语",lt:"立陶宛语",ka:"格鲁吉亚语",hy:"亚美尼亚语",eo:"世界语",he:"希伯来语",yi:"意第绪语",ar:"阿拉伯语",tr:"土耳其语",fa:"波斯语",hi:"印地语",ja:"日语",ko:"韩语",zh:"中文",id:"印尼语",ms:"马来语",tl:"他加禄语",vi:"越南语",th:"泰语",scn:"西西里语",nap:"那不勒斯语",vec:"威尼斯语",lmo:"伦巴第语",oc:"奥克语",eu:"巴斯克语",gl:"加利西亚语",rm:"罗曼什语",af:"南非荷兰语",und:"原文语言"};
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
function normalizeSearch(value=""){
 return String(value).normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLocaleLowerCase().replace(/[’']/g,"").replace(/[^a-z0-9\u3400-\u9fff]+/g," ").trim().replace(/\s+/g," ");
}
function editDistance(a,b,limit){
 const left=Array.from(a),right=Array.from(b);
 if(Math.abs(left.length-right.length)>limit)return limit+1;
 let previous=right.map((_,i)=>i+1);
 previous.unshift(0);
 for(let i=0;i<left.length;i++){
   const current=[i+1];
   let rowMin=current[0];
   for(let j=0;j<right.length;j++){
     current[j+1]=Math.min(current[j]+1,previous[j+1]+1,previous[j]+(left[i]===right[j]?0:1));
     rowMin=Math.min(rowMin,current[j+1]);
   }
   if(rowMin>limit)return limit+1;
   previous=current;
 }
 return previous[right.length];
}
function closeSearchWord(queryWord,candidateWord){
 if(queryWord===candidateWord)return true;
 if(queryWord.length<=3 || candidateWord.length<=3)return false;
 const limit=queryWord.length<=6?1:2;
 return editDistance(queryWord,candidateWord,limit)<=limit;
}
function fuzzyFieldMatch(query,field){
 if(!query||!field)return false;
 if(field.includes(query))return true;
 const queryWords=query.split(" ");
 const fieldWords=field.split(" ");
 if(queryWords.some(word=>/[\u3400-\u9fff]/.test(word)))return false;
 return queryWords.every(word=>fieldWords.some(candidate=>closeSearchWord(word,candidate)));
}
async function loadRepertoire(){
 try{
   const response=await fetch(new URL('data/repertoire.json',sourceRoot),{cache:'no-store'});
   if(!response.ok)throw new Error('HTTP '+response.status);
   const data=await response.json();
   repertoire=data.items||[];
   $('#repertoireCount').textContent=`${repertoire.length} 首已收录`;
   repertoireLoaded=true;
   renderMusicSearch($('#musicSearchInput').value);
 }catch(error){
   repertoireLoaded=false;
   $('#musicSearchResults').innerHTML='<div class="music-empty">曲目库暂时无法更新，请稍后重试。</div>';
 }
}
function keywordContext(item,term){
 const text=(item.text||'').replace(/[ \t]+/g,' ');
 for(const line of text.split('\n')){
   if(normalizeSearch(line).includes(term))return line.trim().slice(0,96);
 }
 return '';
}
function scoreItem(item,terms){
 const title=normalizeSearch(item.title||'');
 const aliases=(item.aliases||[]).map(normalizeSearch);
 const work=normalizeSearch(item.work||'');
 const composer=normalizeSearch(item.composer||'');
 const poet=normalizeSearch(item.poet||'');
 const text=normalizeSearch(item.text||'');
 let best=0,bestTerm='';
 for(const term of terms){
   if(!term)continue;
   let s=0;
   if(title===term)s=100;
   else if(title.startsWith(term))s=80;
   else if(title.split(' ').some(word=>word.startsWith(term)))s=70;
   else if(title.includes(term))s=60;
   else if(work.includes(term)||aliases.some(alias=>alias.includes(term)))s=45;
   else if(composer.includes(term))s=35;
   else if(poet.includes(term))s=25;
   else if(text.includes(term))s=14;
   else if(fuzzyFieldMatch(term,title)||aliases.some(alias=>fuzzyFieldMatch(term,alias)))s=8;
   if(s>best){best=s;bestTerm=term;}
 }
 return {score:best,term:bestTerm};
}
function renderMusicSearch(rawQuery){
 const target=$('#musicSearchResults');
 const query=rawQuery.trim();
 if(!query){
   target.innerHTML='<div class="music-empty">输入歌名、作曲家或唱段首句，边输入边出结果；歌词默认折叠，点“展开全文”再读。</div>';
   return;
 }
 if(!repertoireLoaded){
   target.innerHTML='<div class="music-empty">曲目库正在更新，请稍候。</div>';
   return;
 }
 const terms=query.split(/[\/,，、;；|]+/).map(x=>normalizeSearch(x)).filter(Boolean);
 const scored=repertoire.map(item=>({item,hit:scoreItem(item,terms)}))
   .filter(entry=>entry.hit.score>0)
   .sort((a,b)=>b.hit.score-a.hit.score||a.item.title.localeCompare(b.item.title));
 const total=scored.length;
 const matches=scored.slice(0,12);
 if(!matches.length){
   const near=repertoire.map(item=>({item,sim:editDistance(normalizeSearch(query),normalizeSearch(item.title),6)}))
     .filter(entry=>entry.sim<=6).sort((a,b)=>a.sim-b.sim).slice(0,5);
   target.innerHTML=`<div class="music-empty"><strong>暂未收录“${esc(query)}”</strong><p>曲目库里没有这个词。${near.length?'也许你想找：'+near.map(entry=>`<button type="button" class="search-chip" data-suggest="${esc(entry.item.title)}">${esc(entry.item.title)}</button>`).join(' '):'可以先试短一点的词，例如只输入 nessun、libiamo、amore。'}</p></div>`;
   return;
 }
 const expansions=[...new Set(matches.flatMap(entry=>[entry.item.composer,entry.item.work].filter(Boolean)))].slice(0,6);
 const summary=`<p class="result-meta">共 ${total} 条相关，按匹配程度排序，先显示前 ${matches.length} 条。${expansions.length?'继续检索：':''}${expansions.map(value=>`<button type="button" class="search-chip" data-suggest="${esc(value)}">${esc(value)}</button>`).join(' ')}</p>`;
 target.innerHTML=summary+matches.map(({item,hit})=>{
   const context=hit.score>=14?keywordContext(item,hit.term):'';
   const plain=(item.text||'').replace(/\s+/g,' ').trim();
   const preview=plain.slice(0,110);
   const hasMore=(item.text||'').trim().length>110;
   return `<article class="music-result">
   <div class="music-result-top"><span class="music-kind">${esc(item.kind)}</span><span class="music-voice">${esc(item.voice)}</span></div>
   <h3>${esc(item.title)}</h3>
   <p class="music-byline">${esc([item.composer,item.work?item.work:(item.poet?"词："+item.poet:"")].filter(Boolean).join(" · "))}</p>
   ${context?`<p class="music-hit">“${esc(hit.term)}”出现在原文：${esc(context)}…</p>`:''}
   <div class="music-text"><div class="music-text-label">歌词原文 · ${esc(languageLabel(item.language))}</div><p class="lyrics lyrics-preview">${esc(preview)}${hasMore?'…':''}</p>${hasMore?`<div class="lyrics-full" hidden><p class="lyrics">${esc(item.text).replace(/\n/g,'<br>')}</p></div><button type="button" class="lyrics-toggle" data-open="0">展开全文 ↓</button>`:''}</div>
   <div class="music-reading"><div><span class="music-text-label">泛读 · ${esc(languageLabel(item.language))}</span><p>在 Google 翻译中打开后，点击“听取原文”；会按这首作品的原文语言朗读。</p></div>${googleReadUrl(item)?'<a class="reading-link" href="'+esc(googleReadUrl(item))+'" target="_blank" rel="noopener noreferrer">Google 翻译朗读原文 ↗</a>':'<span class="score-unavailable">文本超过 Google 翻译单次朗读长度</span>'}</div>
   <p class="music-meaning"><strong>大意：</strong>${esc(item.summary)}</p>
   <div class="music-score"><div><span class="music-text-label">乐谱</span><p>${item.downloadUrl?'本站提供已核验的可下载版本。':'本站暂未托管乐谱 PDF。可以先查看 IMSLP 对应作品页；版本与地区版权请自行核对。'}</p></div>${item.downloadUrl?'<a class="score-download" href="'+esc(item.downloadUrl)+'" download>下载乐谱 PDF ↓</a>':item.scoreUrl?'<a class="score-imslp" href="'+esc(item.scoreUrl)+'" target="_blank" rel="noopener noreferrer">IMSLP 查看乐谱 ↗</a>':'<span class="score-unavailable">暂无乐谱链接</span>'}</div>
   <div class="music-source"><span>文本出处：${esc(item.textSourceName||'公开文本来源')} · 本文已收录在本站，搜索和阅读无需跳转。</span></div>
 </article>`;}).join('');
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
let conservatoriData=[];
function renderConservatori(){
 const wrap=$('#conservatori');if(!wrap)return;
 const readable=conservatoriData.filter(c=>c.status==='ok');
 $('#conservatoriCount').textContent=`${readable.length}/${conservatoriData.length}`;
 wrap.innerHTML=conservatoriData.length?conservatoriData.map(c=>{
   const deadlines=(c.deadline_lines||[]).slice(0,2);
   const dates=(c.exam_dates||[]).slice(0,3);
   const reqs=(c.requirements||[]).slice(0,3);
   const docs=(c.documents||[]).slice(0,4);
   return `<article class="cons-card"><div class="cons-head"><h3>${esc(c.city)} · ${esc(c.school)}</h3><span class="status ${c.status==='ok'?'':'error'}">${c.status==='ok'?'已读取官网':'暂时无法读取'}</span></div>${deadlines.length?`<p class="cons-block"><strong>报名期限：</strong>${deadlines.map(esc).join('；')}</p>`:''}${dates.length?`<p class="cons-block"><strong>考试日期：</strong>${dates.map(esc).join('；')}</p>`:''}${reqs.length?`<p class="cons-block"><strong>入学要求：</strong>${reqs.map(esc).join('；')}</p>`:''}${docs.length?`<p class="cons-docs">官方文件：${docs.map(d=>`<a href="${esc(d)}" target="_blank" rel="noopener">PDF</a>`).join(' · ')}</p>`:''}<a class="card-link" href="${esc(c.url)}" target="_blank" rel="noopener">打开学院官网页面 <span>↗</span></a></article>`;
 }).join(''):'<div class="empty">暂时读不到音乐学院数据。</div>';
}
async function loadConservatori(){
 try{
   const res=await fetch(new URL('data/conservatori.json',sourceRoot),{cache:'no-store'});
   if(!res.ok)throw new Error(`HTTP ${res.status}`);
   const data=await res.json();conservatoriData=data.items||[];
 }catch(error){conservatoriData=[];}
 renderConservatori();
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
let musicSearchTimer=null;
$('#musicSearchInput').addEventListener('input',event=>{const value=event.target.value;clearTimeout(musicSearchTimer);musicSearchTimer=setTimeout(()=>renderMusicSearch(value),140);});
document.addEventListener('click',event=>{
 const suggest=event.target.closest('[data-suggest]');
 if(suggest){
   const value=suggest.dataset.suggest||'';
   $('#musicSearchInput').value=value;
   renderMusicSearch(value);
   window.scrollTo({top:document.getElementById('music-library').offsetTop-20,behavior:'smooth'});
   return;
 }
 const toggle=event.target.closest('.lyrics-toggle');
 if(toggle){
   const card=toggle.closest('.music-result');
   const full=card.querySelector('.lyrics-full');
   const preview=card.querySelector('.lyrics-preview');
   const open=toggle.dataset.open==='1';
   if(full)full.hidden=open;
   if(preview)preview.hidden=!open;
   toggle.dataset.open=open?'0':'1';
   toggle.textContent=open?'展开全文 ↓':'收起 ↑';
 }
});
document.querySelectorAll('.search-chip').forEach(button=>button.addEventListener('click',()=>{const q=button.dataset.query;$('#musicSearchInput').value=q;renderMusicSearch(q);}));
renderMusicSearch('');
loadRepertoire();
loadData();
loadConservatori();
