const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const sourceRoot = new URL('.', location.href);

let sourceData = [];
let repertoire = [];
let repertoireLoaded = false;
let conservatoriData = [];
let manualNotes = {};
let consQuery = '';
let consDateOnly = false;
let installPrompt = null;
let openPanelName = null;

const opportunities = [
  {title:'78° Concorso Internazionale AsLiCo per Giovani Cantanti Lirici 2027',category:'歌剧角色招募',place:'科莫 · 多地预选',deadline:'2026-11-25T18:00:00+01:00',summary:'为 2027/28 OperaLombardia 歌剧季选拔演员，也设青年歌手组。招募角色包括《拉美莫尔的露琪亚》《伊多美绚》等；报名费 70 欧元。',url:'https://aslico.org/edizione-in-corso/',source:'AsLiCo'},
  {title:'Concorso Internazionale di Canto lirico Francesco Morlacchi 2026',category:'国际声乐比赛',place:'佩鲁贾',deadline:'2026-11-30T23:59:00+01:00',summary:'比赛将于 2026 年 12 月 14–15 日举行，面呁 18 至 35 岁歌手。报名费 80 欧元，需提交曲目、简历、身份证明及演唱视频。',url:'https://www.concorsomorlacchi.it/',source:'Morlacchi 声乐比赛'}
];

function esc(text=''){return String(text).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
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
  if(queryWord.length<=3||candidateWord.length<=3)return false;
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

/* ---------- dates ---------- */
const MONTHS={gennaio:1,febbraio:2,marzo:3,aprile:4,maggio:5,giugno:6,luglio:7,agosto:8,settembre:9,ottobre:10,novembre:11,dicembre:12};
function isoFromText(text){
  // The closing date is almost always the last date in the sentence.
  const source=String(text||'');
  const slash=[...source.matchAll(/(\d{1,2})\/(\d{1,2})\/(20\d{2})/g)];
  if(slash.length){const m=slash[slash.length-1];return `${m[3]}-${String(m[2]).padStart(2,'0')}-${String(m[1]).padStart(2,'0')}`;}
  const named=[...source.matchAll(/(\d{1,2})\s*(?:º|°)?\s*(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s*(20\d{2})/gi)];
  if(named.length){const m=named[named.length-1];return `${m[3]}-${String(MONTHS[m[2].toLowerCase()]).padStart(2,'0')}-${String(m[1]).padStart(2,'0')}`;}
  const iso=[...source.matchAll(/\b(20\d{2})-(\d{2})-(\d{2})\b/g)];
  if(iso.length){const m=iso[iso.length-1];return `${m[1]}-${m[2]}-${m[3]}`;}
  return '';
}
function zhIsoFromText(text){
  // Chinese binding lines written by hand, e.g. "2027 年 4 月 16–20 日".
  const hits=[...String(text||'').matchAll(/(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})/g)];
  if(!hits.length)return '';
  const m=hits[hits.length-1];
  return `${m[1]}-${String(m[2]).padStart(2,'0')}-${String(m[3]).padStart(2,'0')}`;
}
function zhDate(iso){
  if(!iso)return '';
  const [y,m,d]=iso.split('-');
  return `${y} 年 ${Number(m)} 月 ${Number(d)} 日`;
}
function daysUntil(iso){
  if(!iso)return null;
  const today=new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  const [ty,tm,td]=today.split('-').map(Number);
  const [dy,dm,dd]=iso.split('-').map(Number);
  if(!ty||!dy)return null;
  const diff=Math.round((Date.UTC(dy,dm-1,dd)-Date.UTC(ty,tm-1,td))/86400000);
  return Number.isFinite(diff)?diff:null;
}
function countdown(iso){
  const left=daysUntil(iso);
  if(left===null)return '';
  if(left<0)return ' · 已截止';
  if(left===0)return ' · 今天截止';
  return ` · 剩 ${left} 天`;
}
function formatDate(iso){return new Intl.DateTimeFormat('zh-CN',{timeZone:'Europe/Rome',month:'long',day:'numeric',hour:'2-digit',minute:'2-digit'}).format(new Date(iso));}

/* ---------- repertoire search ---------- */
function itemNorm(item){
  if(!item.__norm){
    item.__norm={
      title:normalizeSearch(item.title||''),
      aliases:(item.aliases||[]).map(normalizeSearch),
      work:normalizeSearch(item.work||''),
      composer:normalizeSearch(item.composer||''),
      poet:normalizeSearch(item.poet||''),
      text:normalizeSearch(item.text||'')
    };
  }
  return item.__norm;
}
function scoreItem(item,terms){
  const {title,aliases,work,composer,poet,text}=itemNorm(item);
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
function keywordContext(item,term){
  const text=(item.text||'').replace(/[ \t]+/g,' ');
  for(const line of text.split('\n')){
    if(normalizeSearch(line).includes(term))return line.trim().slice(0,96);
  }
  return '';
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
    const near=repertoire.map(item=>({item,sim:editDistance(normalizeSearch(query),itemNorm(item).title,6)}))
      .filter(entry=>entry.sim<=6).sort((a,b)=>a.sim-b.sim).slice(0,5);
    target.innerHTML=`<div class="music-empty"><strong>暂未收录“${esc(query)}”</strong><p>曲目库里没有这个词。${near.length?'也许你想找：'+near.map(entry=>`<button type="button" class="search-chip" data-suggest="${esc(entry.item.title)}">${esc(entry.item.title)}</button>`).join(' '):'可以先试短一点的词，例如 nessun、libiamo、amore。'}</p></div>`;
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
   <div class="music-reading"><div><span class="music-text-label">泛读 · ${esc(languageLabel(item.language))}</span><p>在 Google 翻译中打开后，点击“听取原文”；会按这首作品的原文语言阅读。</p></div>${googleReadUrl(item)?'<a class="reading-link" href="'+esc(googleReadUrl(item))+'" target="_blank" rel="noopener noreferrer">Google 翻译朗读原文 ↗</a>':'<span class="score-unavailable">文本超过 Google 翻译单次朗读长度</span>'}</div>
   <p class="music-meaning"><strong>大意：</strong>${esc(item.summary)}</p>
   <div class="music-score"><div><span class="music-text-label">乐谱</span><p>${item.downloadUrl?'本站提供已核验的可下载版本。':'本站暂未托管乐谱 PDF。可以先查看 IMSLP 对应作品页；版本与地区版权请自行核对。'}</p></div>${item.downloadUrl?'<a class="score-download" href="'+esc(item.downloadUrl)+'" download>下载乐谱 PDF ↓</a>':item.scoreUrl?'<a class="score-imslp" href="'+esc(item.scoreUrl)+'" target="_blank" rel="noopener noreferrer">IMSLP 查看乐谱 ↗</a>':'<span class="score-unavailable">暂无乐谱链接</span>'}</div>
   <div class="music-source"><span>文本出处：${esc(item.textSourceName||'公开文本来源')} · 本文已收录在本站，搜索和阅读无需跳转。</span></div>
 </article>`;}).join('');
}
async function loadRepertoire(){
  try{
    const response=await fetch(new URL('data/repertoire.json',sourceRoot),{cache:'no-store'});
    if(!response.ok)throw new Error('HTTP '+response.status);
    const data=await response.json();
    repertoire=data.items||[];
    $('#repertoireCount').textContent=`${repertoire.length} 首已收录`;
    repertoireLoaded=true;
    renderTiles();
    renderMusicSearch($('#musicSearchInput').value);
  }catch(error){
    repertoireLoaded=false;
    $('#musicSearchResults').innerHTML='<div class="music-empty">曲目库暂时无法更新，请稍后重试。</div>';
  }
}

/* ---------- panels ---------- */
function closePanel(){
  openPanelName=null;
  $$('.panel').forEach(panel=>{panel.hidden=true;});
  $$('.tile').forEach(tile=>tile.setAttribute('aria-expanded','false'));
}
function openPanel(name,{scroll=true}={}){
  if(openPanelName===name&&!$('#panel-'+name).hidden){closePanel();return;}
  closePanel();
  const panel=$('#panel-'+name);
  if(!panel)return;
  panel.hidden=false;
  openPanelName=name;
  const tile=$(`.tile[data-panel="${name}"]`);
  if(tile)tile.setAttribute('aria-expanded','true');
  if(scroll)panel.scrollIntoView({behavior:'smooth',block:'start'});
}

/* ---------- open calls ---------- */
function renderCalls(){
  const now=Date.now();
  const derived=conservatoriData.filter(c=>c.manual_status==='open').map(c=>{
    const iso=isoFromText((c.deadline_lines||[]).join(' '));
    if(!iso)return null;
    return {
      title:`${c.city} · ${c.school}`,
      category:'学院报名中',
      place:c.city,
      deadline:`${iso}T23:59:00+01:00`,
      summary:(c.zh&&c.zh.deadline)||(c.deadline_lines||[])[0]||'',
      url:c.manual_source||c.url,
      source:'学院官网'
    };
  }).filter(Boolean);
  const merged=[...derived,...opportunities].sort((a,b)=>new Date(a.deadline)-new Date(b.deadline));
  const current=merged.filter(o=>new Date(o.deadline).getTime()>=now);
  $('#opportunityCount').textContent=`${current.length} 项报名中`;
  $('#opportunities').innerHTML=current.length?current.map(o=>`<article class="opportunity-card"><div class="card-top"><span class="badge">${esc(o.category)}</span><span class="deadline">截止 ${formatDate(o.deadline)}${countdown(String(o.deadline).slice(0,10))}</span></div><h3>${esc(o.title)}</h3><p>${esc(o.summary)}</p><div class="card-meta"><span>⌖ ${esc(o.place)}</span><span>主办方：${esc(o.source)}</span></div><a class="card-link" href="${esc(o.url)}" target="_blank" rel="noopener">查看主办方公告 <span>↗</span></a></article>`).join(''):'<div class="empty">目前没有已确认仍在报名的项目。入学考试板块里还有可以准备的目标。</div>';
  renderTiles();
}

/* ---------- conservatories ---------- */
function fileLabel(url){
  try{
    const raw=decodeURIComponent((url.split('/').pop()||'').split('?')[0]);
    const clean=raw.replace(/\.pdf$/i,'').replace(/[_+]+/g,' ').replace(/\s+/g,' ').trim();
    if(!clean)return 'PDF';
    return clean.length>52?clean.slice(0,52)+'…':clean;
  }catch(error){return 'PDF';}
}
function staleMark(text){
  const years=(String(text||'').match(/\b20\d{2}\b/g)||[]).map(Number);
  if(!years.length)return '';
  return Math.max(...years)<2026?'<span class="cons-stale">旧公告 · 参考价值有限</span>':'';
}
function pickDocs(list){
  const items=(list||[]).map(url=>({url,rank:/bando|ammission|iscrizion/i.test(url)?2:(/calendario|programma|prova|graduator/i.test(url)?1:0)}))
    .sort((a,b)=>b.rank-a.rank||a.url.length-b.url.length);
  const top=items.filter(x=>x.rank===2);
  return (top.length?top.slice(0,2):items.slice(0,3)).map(x=>x.url);
}
function consCard(c){
  const zh=c.zh||{};
  const deadlines=(c.deadline_lines||[]).slice(0,2);
  const dates=(c.exam_dates||[]).slice(0,2);
  const reqs=(c.requirements||[]).slice(0,2);
  const said=[...deadlines,...dates,...reqs].join(' ');
  const soft=(c.fallback_lines||[]).filter(line=>!said.includes(line.slice(0,40))).slice(0,2);
  const docs=pickDocs(c.documents);
  const dlIso=isoFromText(deadlines.join(' '))||zhIsoFromText(zh.deadline||'');
  const exIso=isoFromText(dates.join(' '))||zhIsoFromText(zh.exam||'');
  const closed=c.manual_status==='closed';
  const parts=[];
  if(dlIso)parts.push(`报名截止 ${zhDate(dlIso)}${closed?'（已截止）':''}`);
  if(exIso)parts.push(`考试 ${zhDate(exIso)}${closed?'（已截止）':''}`);
  const summary=parts.length?parts.join(' · '):(zh.note||soft[0]||'官网本季未公布日期');
  const badge=c.manual_status==='open'?`<span class="badge badge--gold">报名进行中${countdown(dlIso)}</span>`:'';
  const zhBlocks=[
    zh.deadline?`<p><strong>报名</strong>${esc(zh.deadline)}</p>`:'',
    zh.exam?`<p><strong>考试</strong>${esc(zh.exam)}</p>`:'',
    zh.requirements?`<p><strong>要求</strong>${esc(zh.requirements)}</p>`:'',
    zh.note?`<p><strong>备注</strong>${esc(zh.note)}</p>`:''
  ].join('');
  const origBlocks=[
    deadlines.length?`<strong>报名期限（原文）</strong><br>${deadlines.map(esc).join('<br>')}`:'',
    dates.length?`<strong>考试日期（原文）</strong><br>${dates.map(esc).join('<br>')}`:'',
    reqs.length?`<strong>入学要求（原文）</strong><br>${reqs.map(esc).join('<br>')}`:'',
    (!zh.note&&soft.length)?`<strong>页面要点（原文）</strong><br>${soft.map(esc).join('<br>')}`:''
  ].filter(Boolean).join('<br><br>');
  return `<article class="cons-card${c.number>=300?' cons-card--academy':''}">
   <div class="cons-head"><h3>${esc(c.city)}<small>${esc(c.school)}</small></h3><span class="status ${c.status==='ok'?'':'error'}">${c.status==='ok'?(c.cached?'上次读取':'官网可读'):'暂时读不到'}</span></div>
   ${badge?`<div>${badge}</div>`:''}
   <p class="cons-sum">${esc(summary)}</p>
   <details class="cons-more"><summary>中文要点 · 原文 · 官方简章</summary>
     ${zhBlocks?`<div class="cons-zh">${zhBlocks}</div>`:''}
     ${origBlocks?`<div class="cons-orig">${origBlocks}</div>`:''}
     ${docs.length?`<p class="cons-docs"><strong>官方简章</strong>${docs.map(d=>`<a class="doc-link" href="${esc(d)}" target="_blank" rel="noopener">${esc(fileLabel(d))} ↗</a>`).join('')}</p>`:''}
     <p class="cons-docs"><a class="doc-link" href="${esc(c.url)}" target="_blank" rel="noopener">打开学院官网 ↗</a></p>
   </details>
 </article>`;
}
function renderConservatori(){
  const wrap=$('#consGroups');
  if(!wrap)return;
  const readable=conservatoriData.filter(c=>c.status==='ok');
  $('#conservatoriCount').textContent=`${readable.length}/${conservatoriData.length}`;
  const q=normalizeSearch(consQuery);
  const filtered=conservatoriData.filter(c=>{
    if(q&&!normalizeSearch(`${c.city||''} ${c.school||''}`).includes(q))return false;
    if(consDateOnly&&!((c.deadline_lines||[]).length||(c.exam_dates||[]).length))return false;
    return true;
  }).sort((a,b)=>{
    const oa=a.manual_status==='open'?1:0,ob=b.manual_status==='open'?1:0;
    if(ob!==oa)return ob-oa;
    const da=(a.deadline_lines||[]).length+(a.exam_dates||[]).length;
    const db=(b.deadline_lines||[]).length+(b.exam_dates||[]).length;
    if(db!==da)return db-da;
    return String(a.city||'').localeCompare(String(b.city||''),'zh');
  });
  const groups=[
    {title:'歌剧院学院',hint:'Teatro · Accademia',items:filtered.filter(c=>(c.number||0)>=300)},
    {title:'公立音乐学院',hint:'Conservatorio',items:filtered.filter(c=>(c.number||0)<300)}
  ].filter(g=>g.items.length);
  wrap.innerHTML=groups.map(g=>`<section class="cons-group"><div class="cons-group-head"><h3>${g.title}</h3><span>${g.hint} · ${g.items.length} 所</span></div><div class="cons-list">${g.items.map(consCard).join('')}</div></section>`).join('');
  const emptyBox=$('#conservatoriEmpty');
  if(emptyBox)emptyBox.innerHTML=filtered.length?'':'<div class="empty">没有符合条件的院校。换个城市名，或关掉“只看有日期”。</div>';
  renderTiles();
}

/* ---------- theatres ---------- */
const THEATRE_RE=/teatro|teatri|opera|operahouse|festival|accademia|conservatorio|regio|massimo|carlofelice|coccia|sancarlo|rossini|maggio|aslico|compagnia/i;
function renderTheatres(){
  const q=$('#searchInput')?$('#searchInput').value.trim().toLocaleLowerCase():'';
  const rows=sourceData.filter(s=>{
    const hay=`${s.source||''} ${s.url||''}`;
    if(!THEATRE_RE.test(hay))return false;
    if(q&&!`${s.source} ${s.title} ${(s.relevant_lines||[]).join(' ')}`.toLocaleLowerCase().includes(q))return false;
    return true;
  });
  $('#sourceCount').textContent=`${rows.length} 家`;
  $('#sources').innerHTML=rows.length?`<div class="flow">${rows.map(s=>{
    const lines=(s.relevant_lines||[]).filter(x=>!x.includes('Privacy')&&!x.includes('cookie')).slice(0,2);
    const stamp=s.checked_at?new Intl.DateTimeFormat('zh-CN',{timeZone:'Europe/Rome',dateStyle:'medium',timeStyle:'short'}).format(new Date(s.checked_at)):'—';
    return `<article class="flow-card"><h3><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.source)} ↗</a></h3>${lines.length?`<p>${esc(lines.join(' · '))}</p>`:'<p>这次没有找到可展示的招募内容。</p>'}<div class="flow-meta"><span>${s.status==='ok'?'页面可访问':'暂时无法读取 '+(s.http_status||'')}</span><span>最近查看 ${stamp}</span></div></article>`;
  }).join('')}</div>`:'<div class="empty">没有符合条件的剧院。</div>';
  renderTiles();
}

function renderTiles(){
  const callsCount=$('#opportunities')?$('#opportunities').querySelectorAll('.opportunity-card').length:0;
  const totalCon=conservatoriData.length;
  const readable=conservatoriData.filter(c=>c.status==='ok').length;
  const theatres=sourceData.filter(s=>THEATRE_RE.test(`${s.source||''} ${s.url||''}`)).length;
  $('#tileCalls').textContent=callsCount?`${callsCount} 项报名中`:'暂无开放报名';
  $('#tileExam').textContent=totalCon?`${totalCon} 所 · ${readable} 可读`:'读取中…';
  $('#tileMusic').textContent=repertoireLoaded?`${repertoire.length} 首`:'读取中…';
  $('#tileTeatro').textContent=theatres?`${theatres} 家机构`:'读取中…';
}

/* ---------- loading ---------- */
async function loadConservatori(){
  try{
    const [res,manual]=await Promise.all([
      fetch(new URL('data/conservatori.json',sourceRoot),{cache:'no-store'}),
      fetch(new URL('data/conservatori_manual.json',sourceRoot),{cache:'no-store'}).catch(()=>null)
    ]);
    if(!res.ok)throw new Error(`HTTP ${res.status}`);
    const data=await res.json();
    conservatoriData=data.items||[];
    if(manual&&manual.ok){
      const m=await manual.json();
      manualNotes={};
      for(const entry of m.items||[])manualNotes[entry.number]=entry;
      for(const item of conservatoriData){
        const note=manualNotes[item.number];
        if(note&&note.zh)item.zh=note.zh;
      }
    }
  }catch(error){conservatoriData=[];}
  renderConservatori();
  renderCalls();
}
async function loadData(){
  $('#updatedAt').textContent='正在更新来源动态…';
  try{
    const res=await fetch(new URL('data/sources.json',sourceRoot),{cache:'no-store'});
    if(!res.ok)throw new Error(`HTTP ${res.status}`);
    const data=await res.json();
    sourceData=data.sources||data;
    const checked=data.generated_at||sourceData[0]?.checked_at;
    $('#updatedAt').textContent=checked?`最近查看：${new Intl.DateTimeFormat('zh-CN',{timeZone:'Europe/Rome',dateStyle:'medium',timeStyle:'short'}).format(new Date(checked))}`:'数据已更新';
  }catch(error){
    $('#updatedAt').textContent='暂时无法更新数据';
    sourceData=[];
  }
  renderTheatres();
  renderCalls();
}

/* ---------- wiring ---------- */
$$('.tile').forEach(tile=>tile.addEventListener('click',()=>openPanel(tile.dataset.panel)));
$$('.nav-link').forEach(link=>link.addEventListener('click',()=>openPanel(link.dataset.panel)));
$$('.panel-close').forEach(button=>button.addEventListener('click',()=>{closePanel();$('#tiles').scrollIntoView({behavior:'smooth',block:'start'});}));
$('#refreshButton').addEventListener('click',()=>{loadData();loadConservatori();loadRepertoire();});
$('#searchInput').addEventListener('input',renderTheatres);
const consInput=$('#consSearchInput');
if(consInput)consInput.addEventListener('input',event=>{consQuery=event.target.value;renderConservatori();});
const consToggle=$('#consDateOnly');
if(consToggle)consToggle.addEventListener('click',()=>{consDateOnly=!consDateOnly;consToggle.setAttribute('aria-pressed',String(consDateOnly));renderConservatori();});
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
    $('#panel-music').scrollIntoView({behavior:'smooth',block:'start'});
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
$$('.search-chip').forEach(button=>button.addEventListener('click',()=>{const q=button.dataset.query;$('#musicSearchInput').value=q;renderMusicSearch(q);}));
renderMusicSearch('');
renderTiles();
loadRepertoire();
loadData();
loadConservatori();
