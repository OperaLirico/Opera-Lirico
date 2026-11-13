const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const sourceRoot = new URL('.', location.href);

/* Styles for the extra "this word also appears in the lyrics" group. */
(function searchExtraStyles(){
  if(document.getElementById('search-extra-styles'))return;
  const style=document.createElement('style');
  style.id='search-extra-styles';
  style.textContent='.music-extra{margin-top:18px;border:1px dashed var(--line);border-radius:12px;padding:0 16px;background:var(--paper-2)}'
    +'.music-extra summary{cursor:pointer;padding:13px 0;font-size:12px;color:var(--ink-soft);list-style:none}'
    +'.music-extra summary::-webkit-details-marker{display:none}'
    +'.music-extra[open] summary{border-bottom:1px solid var(--line)}'
    +'.music-extra-body{padding:12px 0 14px;display:flex;flex-direction:column;gap:14px}'
    +'.music-extra-row{display:flex;flex-direction:column;gap:3px}'
    +'.music-extra-row strong{font-family:var(--serif);font-size:15px;font-weight:600}'
    +'.music-match-line{font-size:12px;color:var(--ink-soft);line-height:1.6}'
    +'.music-extra-row .search-chip{align-self:flex-start;margin-top:2px}';
  document.head.appendChild(style);
})();

let repertoire = [];
let repertoireLoaded = false;
let conservatoriData = [];
let manualNotes = {};
let zhNotes = {};
let consQuery = '';
let consDateOnly = false;
let academyQuery = '';
let academyDateOnly = false;
let installPrompt = null;

let opportunities = [];

function esc(text=''){return String(text).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
/* 抓下来的记录里，work 位置偶尔存的是目录路径、poet 位置存的是译者署名，都不是我们能展示的东西。 */
function cleanName(value){
  const text=String(value||'')
    .replace(/(?:https?:\/\/)?\S*\/lieder\/\S*|\S*\.html\?\S*/gi,' ')
    .replace(/\s{2,}/g,' ')
    .replace(/^[·,;:\-]+|[·,;:\-]+$/g,'')
    .trim();
  if(!text)return '';
  if(/^\/|^http|\?/.test(text))return '';
  return text;
}
function poetOf(item){
  const poet=cleanName(item.poet);
  if(!poet)return '';
  if(/translation|translated|possibly|unknown|anonymous|attributed/gi.test(poet))return '';
  if(/^from /i.test(poet))return '';
  if(poet.length>26)return '';
  return poet;
}
function bylineOf(item){
  const work=cleanName(item.work);
  const poet=poetOf(item);
  return [cleanName(item.composer),work||(poet?'词：'+poet:'')].filter(Boolean).join(' · ');
}
/* 文本来源偶尔存的是乐谱站地址，那就不要说成“原文来自” */
function sourceNoteOf(item){
  const name=cleanName(item.textSourceName||'').replace(/原文$/,'').trim();
  if(/IMSLP|imslp/i.test(name))return '乐谱链接指向 IMSLP 作品页。';
  return `文本来源：${name||'公开文本来源'}。`;
}
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

/* 把英文日期、冗余前缀改成人话再上屏 */
function humanText(value){
  let text=String(value||'').trim();
  text=text.replace(/^(报名申请|报名截止日期|报名截止|报名时间|注册申请截止日期|注册报名截止日期|入学考试|声乐入学考试|考试日期|考试时间|报名|考试|要求)：/,'');
  text=text.replace(/(20\d{2})-(\d{2})-(\d{2})/g,(m,y,mo,d)=>`${y} 年 ${Number(mo)} 月 ${Number(d)} 日`);
  text=text.replace(/（已截止）/g,'，已过');
  return text;
}

/* ---------- repertoire search ---------- */
function itemNorm(item){
  if(!item.__norm){
    item.__norm={
      title:normalizeSearch(item.title||''),
      aliases:(item.aliases||[]).map(normalizeSearch),
      work:normalizeSearch(cleanName(item.work||'')),
      composer:normalizeSearch(cleanName(item.composer||'')),
      poet:normalizeSearch(poetOf(item)),
      text:normalizeSearch(item.text||'')
    };
  }
  return item.__norm;
}
function hasWord(field,term){
  if(!field||!term)return false;
  if(/[\u3400-\u9fff]/.test(term))return field.includes(term);
  const words=field.split(' ');
  if(words.includes(term))return true;
  if(term.length>=5&&words.some(word=>word.startsWith(term)))return true;
  return false;
}
function scoreName(item,term){
  if(!term)return 0;
  const n=itemNorm(item);
  if(n.title===term)return 100;
  if(n.aliases.some(alias=>alias===term))return 94;
  if(n.title.startsWith(term))return 88;
  if(n.aliases.some(alias=>alias&&alias.startsWith(term)))return 80;
  if(term.length>=3&&n.title.split(' ').some(word=>word.startsWith(term)))return 74;
  if(term.length>=4&&n.title.includes(term))return 68;
  if(n.work&&hasWord(n.work,term))return 60;
  if(n.aliases.some(alias=>alias&&alias.includes(term)))return 54;
  if(n.composer&&hasWord(n.composer,term))return 44;
  if(n.poet&&hasWord(n.poet,term))return 34;
  if(fuzzyFieldMatch(term,n.title)||n.aliases.some(alias=>fuzzyFieldMatch(term,alias)))return 12;
  return 0;
}
function textHit(item,term){
  const normalized=itemNorm(item).text;
  if(!normalized||!term)return null;
  const words=normalized.split(' ');
  let count=0;
  if(words.includes(term))count=words.filter(word=>word===term).length;
  else if(term.length>=5)count=words.filter(word=>word.startsWith(term)).length;
  if(!count)return null;
  const lines=(item.text||'').replace(/\t/g,' ').split('\n');
  let line='';
  for(const raw of lines){
    const nl=normalizeSearch(raw);
    if(!nl)continue;
    const lw=nl.split(' ');
    if(lw.includes(term)||(term.length>=5&&lw.some(word=>word.startsWith(term)))){line=raw.trim().slice(0,96);break;}
  }
  return {count,line:line||(item.text||'').replace(/\s+/g,' ').slice(0,96)};
}
function matchItem(item,terms){
  let nameScore=101, hitTerm='', firstText=null, matched=true;
  for(const term of terms){
    const ns=scoreName(item,term);
    const th=textHit(item,term);
    if(!ns&&!th){matched=false;break;}
    if(ns){if(ns<nameScore){nameScore=ns;hitTerm=term;}}
    else nameScore=0;
    if(th&&!firstText)firstText=th;
  }
  if(!matched)return null;
  return {item,nameScore:nameScore>=101?0:nameScore,term:hitTerm||terms[0],text:firstText};
}
/* 占位式的“大意”字串不展示；只有真正写过中文大意的才出这一段 */
function summaryOf(item){
  const text=String(item.summary||'').trim();
  if(!text)return '';
  if(/尚未人工翻译|LiederNet 收录的声乐文本/.test(text))return '';
  return text;
}
const voicePatterns={tenor:/男高音|tenor/i,soprano:/女高音|soprano/i,mezzo:/女中音|mezzo/i,baritone:/男中音|baritone/i,bass:/男低音|basso|bass/i,contralto:/女低音|contralto/i};
function matchesVoiceFilter(item,filter){return filter==='all'||Boolean((voicePatterns[filter]||/$a/).test(String(item.voice||'')));}
function renderMusicSearch(rawQuery){
  const target=$('#musicSearchResults');
  const query=rawQuery.trim();
  const voiceFilter=$('#musicVoiceFilter')?.value||'all';
  const visibleRepertoire=repertoire.filter(item=>matchesVoiceFilter(item,voiceFilter));
  if(!query){
    if(!visibleRepertoire.length){target.innerHTML='<div class="music-empty">这个声部暂时没有收录曲目。可以切换到“全部声部”查看完整曲库。</div>';return;}
    const groups=[...new Set(visibleRepertoire.filter(item=>item.section).map(item=>item.section))];
    const featured=groups.map(group=>{
      const items=visibleRepertoire.filter(item=>item.section===group).sort((a,b)=>(a.priority||999)-(b.priority||999));
      return items.length?'<section class="music-feature-group"><h3>'+esc(group)+'</h3><div class="music-feature-list">'+items.map(item=>'<button type="button" class="music-feature-item" data-suggest="'+esc(item.title)+'"><strong>'+esc(item.title)+'</strong><span>'+esc(cleanName(item.composer||''))+'</span></button>').join('')+'</div></section>':'';
    }).join('');
    target.innerHTML='<p class="result-meta">先浏览常见、经典的声乐曲目；输入作品名或作曲家可搜索。冷门自动导入记录已从主曲库分离。</p>'+featured;
    return;
  }
  if(!repertoireLoaded){
    target.innerHTML='<div class="music-empty">正在载入曲目资料，请稍候。</div>';
    return;
  }
  const terms=query.split(/[\/,，、;；|]+/).map(normalizeSearch).filter(Boolean);
  const evaluated=visibleRepertoire.map(item=>matchItem(item,terms)).filter(Boolean);
  const main=evaluated.filter(entry=>entry.nameScore>0)
    .sort((a,b)=>b.nameScore-a.nameScore||(a.item.priority||9999)-(b.item.priority||9999)||a.item.title.localeCompare(b.item.title));
  const extra=evaluated.filter(entry=>!entry.nameScore)
    .sort((a,b)=>((b.text&&b.text.count)||0)-((a.text&&a.text.count)||0)||a.item.title.localeCompare(b.item.title));
  if(!evaluated.length){
    const near=visibleRepertoire.map(item=>({item,sim:editDistance(normalizeSearch(query),itemNorm(item).title,6)}))
      .filter(entry=>entry.sim<=6).sort((a,b)=>a.sim-b.sim).slice(0,5);
    target.innerHTML=`<div class="music-empty"><strong>未找到“${esc(query)}”</strong><p>${near.length?'你可能想找：'+near.map(entry=>`<button type="button" class="search-chip" data-suggest="${esc(entry.item.title)}">${esc(entry.item.title)}</button>`).join(' '):'请尝试缩短关键词，或使用作品名称、作曲家姓名进行搜索。'}</p></div>`;
    return;
  }
  const shown=main.slice(0,12);
  const chips=[...new Set(shown.flatMap(entry=>[cleanName(entry.item.composer),cleanName(entry.item.work)]).filter(value=>value&&value.length<=38))].slice(0,4);
  const bits=[];
  bits.push(main.length?`作品名称或别名匹配 ${main.length} 首`:'未匹配到作品名称或别名');
  if(main.length>shown.length)bits.push(`先看前 ${shown.length} 首`);
  if(extra.length)bits.push(`另有 ${extra.length} 首在歌词中匹配`);
  const head=`<p class="result-meta">${bits.join(' · ')}${chips.length&&shown.length?' · 接着搜：':''}${shown.length?chips.map(value=>`<button type="button" class="search-chip" data-suggest="${esc(value)}">${esc(value)}</button>`).join(' '):''}</p>`;
  const cards=shown.map(entry=>{
    const item=entry.item;
    const plain=(item.text||'').replace(/\s+/g,' ').trim();
    const preview=plain.slice(0,110);
    const hasMore=(item.text||'').trim().length>110;
    const readLink=plain?googleReadUrl(item):'';
    const summary=summaryOf(item);
    const tags=[item.kind,item.voice].filter(value=>value&&value!=='待分类');
    return `<article class="music-result">
   ${tags.length?`<div class="music-result-top">${tags.map(value=>`<span class="music-kind">${esc(value)}</span>`).join('')}</div>`:''}
   <h3>${esc(item.title)}</h3>
   <p class="music-byline">${esc(bylineOf(item))}</p>
   <div class="music-text"><div class="music-text-label">作品原文 · ${esc(languageLabel(item.language))}</div><p class="lyrics lyrics-preview">${plain?esc(preview)+(hasMore?'…':''):'原文暂未收录，先查看作品信息与来源说明。'}</p>${hasMore?`<div class="lyrics-full" hidden><p class="lyrics">${esc(item.text).replace(/\n/g,'<br>')}</p></div><button type="button" class="lyrics-toggle" data-open="0" >展开完整文本 ↓</button>`:''}</div>
   <div class="music-reading"><div><span class="music-text-label">原文发音</span><p>打开 Google 翻译后，点击扬声器即可收听原文发音。</p></div>${readLink?'<a class="reading-link" href="'+esc(readLink)+'" target="_blank" rel="noopener noreferrer" >收听原文发音 ↗</a>':'<span class="score-unavailable">'+(plain?'文本较长，无法直接生成朗读':'原文未收录，暂不提供朗读')+'</span>'}</div>
   ${summary?`<p class="music-meaning"><strong>大意：</strong>${esc(summary)}</p>`:''}
   <div class="music-score"><div><span class="music-text-label">乐谱</span><p>${item.downloadUrl?'此版本已核对，可下载。':'本站暂未提供乐谱文件。可前往 IMSLP 查看相关版本，并留意作品及版本的版权信息。'}</p></div>${item.downloadUrl?'<a class="score-download" href="'+esc(item.downloadUrl)+'" download>下载乐谱 PDF ↓</a>':item.scoreUrl?'<a class="score-imslp" href="'+esc(item.scoreUrl)+'" target="_blank" rel="noopener noreferrer">IMSLP 查看乐谱 ↗</a>':'<span class="score-unavailable" >暂未收录乐谱链接</span>'}</div>
   <div class="music-source"><span>${esc(sourceNoteOf(item))}</span>${item.attributionNote?`<p class="music-match-line">${esc(item.attributionNote)}</p>`:''}</div>
 </article>`;
  }).join('');
  const extraBlock=extra.length?`<details class="music-extra"><summary>歌词中也有匹配：${extra.length} 首（展开查看对应句子）</summary><div class="music-extra-body">${extra.slice(0,12).map(entry=>{const item=entry.item;const line=entry.text?entry.text.line:'';return `<div class="music-extra-row"><strong>${esc(item.title)}</strong><span class="music-byline">${esc(bylineOf(item))}</span><p class="music-match-line">${esc(line)}</p><button type="button" class="search-chip" data-suggest="${esc(item.title)}" >查看完整文本</button></div>`;}).join('')}${extra.length>12?`<p class="music-match-line">另有 ${extra.length-12} 首未显示。可增加关键词缩小范围。</p>`:''}</div></details>`:'';
  target.innerHTML=head+cards+extraBlock;
}
async function loadRepertoire(){
  try{
    const response=await fetch(new URL('data/repertoire.json',sourceRoot),{cache:'no-store'});
    if(!response.ok)throw new Error('HTTP '+response.status);
    const data=await response.json();
    repertoire=data.items||[];
    $('#repertoireCount').textContent=`${repertoire.length} 首`;
    repertoireLoaded=true;
    renderTiles();
    renderMusicSearch($('#musicSearchInput').value);
  }catch(error){
    repertoireLoaded=false;
    $('#musicSearchResults').innerHTML='<div class="music-empty">暂时无法载入曲目资料，请稍后重新载入。</div>';
  }
}

/* ---------- panels ---------- */
function closePanels(){
  $$('.panel').forEach(panel=>{panel.hidden=true;});
}
function openPanel(name,{scroll=true}={}){
  const target=document.getElementById(name);
  if(!target)return;
  closePanels();
  target.hidden=false;
  if(scroll)target.scrollIntoView({behavior:'smooth',block:'start'});
}
function backToTiles(){
  closePanels();
  const tiles=$('#tiles');
  if(tiles)tiles.scrollIntoView({behavior:'smooth',block:'start'});
}

/* ---------- open calls ---------- */
function publishedOpportunity(record){
  if(record.publication_status!=='published'||record.review_status!=='verified'||record.publisher_status!=='official')return null;
  const deadline=record.application_deadline_at;
  if(!deadline||!Number.isFinite(Date.parse(deadline))||Date.parse(deadline)<Date.now())return null;
  const categories={opera_role:'歌剧角色招募',choir:'合唱团招募',vocal_competition:'国际声乐比赛',young_artist:'青年艺术家项目',conservatory_admission:'音乐学院招生',other_vocal:'声乐机会'};
  const voices=(record.voice_types||[]).map(v=>({soprano:'女高音',mezzo_soprano:'女中音',contralto:'女低音',countertenor:'假声男高音',tenor:'男高音',baritone:'男中音',bass:'男低音',all_voices:'不限声部',unspecified:'声部未注明'}[v]||v));
  const details=[record.eligibility_summary,voices.length?`声部：${voices.join('、')}`: '',record.fee_eur!=null?(record.fee_eur===0?'报名费：免费':`报名费：€${record.fee_eur}`):'',record.audition_start_at?`试唱/比赛：${formatDate(record.audition_start_at)}${record.audition_end_at&&record.audition_end_at.slice(0,10)!==record.audition_start_at.slice(0,10)?' 至 '+formatDate(record.audition_end_at):''}`: '',record.notes?`说明：${record.notes}`: ''].filter(Boolean);
  return {title:record.title_zh||record.title,originalTitle:record.title_zh?record.title:'',category:categories[record.opportunity_type]||'声乐机会',place:record.location||'地点以公告为准',deadline,summary:details.join('；')||'详情请以主办方公告为准。',url:record.announcement_url,applicationUrl:record.application_url,officialPdfUrl:record.official_pdf_url,source:record.source_name};
}
function renderCalls(){
  const now=Date.now();
  const managedSchoolSources=new Set(opportunities.filter(o=>['young_artist','conservatory_admission'].includes(o.opportunity_type)).map(o=>o.source_url));
  const derived=conservatoriData.filter(c=>c.manual_status==='open'&&!managedSchoolSources.has(c.manual_source||c.url)).map(c=>{
    const iso=isoFromText((c.deadline_lines||[]).join(' '));
    if(!iso)return null;
    return {
      title:`${c.city} · ${c.school}`,
      category:'学院报名中',
      place:c.city,
      deadline:`${iso}T23:59:00+01:00`,
      summary:(c.zh&&((c.zh.d||[])[0]||(c.zh.x||[])[0]))||(c.deadline_lines||[])[0]||'',
      url:c.manual_source||c.url,
      source:'学院官网'
    };
  }).filter(Boolean);
  const verified=opportunities.map(publishedOpportunity).filter(Boolean);
  const merged=[...derived,...verified].sort((a,b)=>new Date(a.deadline)-new Date(b.deadline));
  const current=merged.filter(o=>new Date(o.deadline).getTime()>=now);
  const pill=$('#opportunityCount');
  if(pill)pill.textContent=`${current.length} 项开放报名`;
  const box=$('#opportunities');
  if(box)box.innerHTML=current.length?current.map(o=>`<article class="opportunity-card"><div class="card-top"><span class="badge">${esc(o.category)}</span><span class="deadline">报名截止：${formatDate(o.deadline)}${countdown(String(o.deadline).slice(0,10))}</span></div><h3>${esc(o.title)}</h3>${o.originalTitle?`<p class="opportunity-original">${esc(o.originalTitle)}</p>`:'' }<p>${esc(humanText(o.summary))}</p><div class="card-meta"><span>⌖ ${esc(o.place)}</span><span>${esc(o.source)}</span></div><a class="card-link" href="${esc(o.url)}" target="_blank" rel="noopener">查看主办方公告 <span>↗</span></a>${o.applicationUrl?`<a class="card-link" href="${esc(o.applicationUrl)}" target="_blank" rel="noopener">在线申请 <span>↗</span></a>`:'' }${o.officialPdfUrl?`<a class="card-link" href="${esc(o.officialPdfUrl)}" target="_blank" rel="noopener">下载官方简章 PDF <span>↗</span></a>`:''}</article>`).join(''):'<div class="empty">现在没有确认在招的项目。可以先看考试那栏，挑几个能提前准备的。</div>';
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
  return Math.max(...years)<2026?'<span class="cons-stale">往年公告，仅供参考</span>':'';
}
function isExpiredAcademicSnippet(text){
  const value=String(text||'');
  const ranges=[...value.matchAll(/\b(20\d{2})\s*[-/–]\s*(?:(20)?(\d{2}))\b/g)];
  if(ranges.length){
    return ranges.every(match=>{
      const endYear=match[2]?Number(match[2]+match[3]):Number(match[1].slice(0,2)+match[3]);
      return endYear<2027;
    });
  }
  const years=(value.match(/\b20\d{2}\b/g)||[]).map(Number);
  return years.length>0&&Math.max(...years)<2026;
}
function visibleCurrentLines(lines){
  return (lines||[]).filter(line=>!isExpiredAcademicSnippet(line));
}
function currentDocs(list){
  return (list||[]).filter(url=>{
    const years=(String(url).match(/20\d{2}/g)||[]).map(Number);
    return !years.length || Math.max(...years)>=2026;
  });
}
function pickDocs(list){
  const items=currentDocs(list).filter(url=>!/guida-dsa|dsa|accessibilit|english|inglese/i.test(url))
    .map(url=>({url,rank:/bando|ammission|iscrizion/i.test(url)?2:(/calendario|programma|prova|gradando|graduatori/i.test(url)?1:0)}))
    .sort((a,b)=>b.rank-a.rank||a.url.length-b.url.length);
  const top=items.filter(x=>x.rank===2);
  return (top.length?top.slice(0,2):items.slice(0,3)).map(x=>x.url);
}
function localPdfs(c){
  const list=[];
  if(c.pdf_local)list.push(c.pdf_local);
  for(const extra of c.pdf_locals||[])if(!list.includes(extra))list.push(extra);
  return currentDocs(list);
}
function stateLabel(state){
  const map={
    '有窗口':'已公布报名日期','只有要求':'仅有申请条件','只有大纲':'仅有考试大纲',
    '非招生页':'非招生信息','读不到':'暂无法读取','可读':'页面可正常读取',
    '报名中':'开放报名','已截止':'报名已截止','未公布':'尚未公布',
    '上期已截止':'上一期已截止','有日期':'已公布考试日期','待核实':'待核实',
    '只有课程':'仅有课程介绍','有安排':'已公布考试安排','只有规则':'仅有注册规则',
    '有公告':'已发布招生公告','旧公告':'仅有往年公告'
  };
  return map[state]||state;
}
function stateClass(state=''){
  if(/报名中|开放报名/.test(state))return 'state--open';
  if(/已截止|上期已截止|上一期已截止|旧公告/.test(state))return 'state--closed';
  if(/读不到|暂无法读取/.test(state))return 'state--offline';
  return 'state--neutral';
}
function consLine(c){
  const zh=c.zh||{};
  const deadlineLines=visibleCurrentLines(c.deadline_lines);
  const examDates=visibleCurrentLines(c.exam_dates);
  const zhDeadlines=visibleCurrentLines(zh.d);
  const zhExamDates=visibleCurrentLines(zh.x);
  const zhRequirements=visibleCurrentLines(zh.r);
  const dl=zh.deadline_iso||isoFromText(deadlineLines.join(' '))||zhIsoFromText(zhDeadlines.join(' '));
  const ex=zh.exam_iso||isoFromText(examDates.join(' '))||zhIsoFromText(zhExamDates.join(' '));
  const bits=[];
  if(dl)bits.push(`报名截止：${zhDate(dl)}${daysUntil(dl)<0?'（已截止）':countdown(dl).replace(/^ · /,'（') + '）'}`);
  if(ex)bits.push(`考试日期：${zhDate(ex)}`);
  if(bits.length)return bits.join(' · ');
  if(zhDeadlines.length)return humanText(zhDeadlines[0]).slice(0,60);
  if(zhExamDates.length)return humanText(zhExamDates[0]).slice(0,60);
  if(zhRequirements.length)return humanText(zhRequirements[0]).slice(0,60);
  return c.status==='ok'?'暂未找到本学年的具体日期，请查看院校官网公告。':'本次未能读取官网内容，可前往院校官网查看。';
}
function consCard(c){
  const zh=c.zh||{};
  const state=zh.state||(c.manual_status==='open'?'报名中':c.manual_status==='closed'?'已截止':c.status==='ok'?'可读':'读不到');
  const rawLines=[...(c.deadline_lines||[]),...(c.exam_dates||[]),...(c.requirements||[]),...(c.fallback_lines||[]),...(zh.d||[]),...(zh.x||[]),...(zh.r||[]),...(zh.notes||[])];
  const hasHiddenHistory=rawLines.some(isExpiredAcademicSnippet);
  const deadlines=visibleCurrentLines(c.deadline_lines).slice(0,2);
  const dates=visibleCurrentLines(c.exam_dates).slice(0,2);
  const reqs=visibleCurrentLines(c.requirements).slice(0,2);
  const zhDeadlines=visibleCurrentLines(zh.d);
  const zhExamDates=visibleCurrentLines(zh.x);
  const zhRequirements=visibleCurrentLines(zh.r);
  const zhNotes=visibleCurrentLines(zh.notes);
  const said=[...deadlines,...dates,...reqs].join(' ');
  const soft=visibleCurrentLines(c.fallback_lines).filter(line=>!/[\u3400-\u9fff]/.test(line)&&!said.includes(line.slice(0,40))).slice(0,2);
  const docs=pickDocs(c.documents);
  const locals=localPdfs(c);
  const zhBlocks=[
    zhDeadlines.length?`<p><span class="zh-key">报名安排</span>${zhDeadlines.map(v=>esc(humanText(v))).join('<br>')}</p>`:'',
    zhExamDates.length?`<p><span class="zh-key">考试安排</span>${zhExamDates.map(v=>esc(humanText(v))).join('<br>')}</p>`:'',
    zhRequirements.length?`<p><span class="zh-key">申请条件</span>${zhRequirements.map(v=>esc(humanText(v))).join('<br>')}</p>`:'',
    zhNotes.length?`<p><span class="zh-key">补充说明</span>${zhNotes.map(v=>esc(humanText(v))).join('<br>')}</p>`:'',
    hasHiddenHistory?`<p><span class="zh-key">历史信息</span>检测到往年招生摘录，已从当前信息区隐藏；请以院校官网最新公告为准。</p>`:''
  ].filter(Boolean).join('');
  const origBlocks=[
    deadlines.length?`<span class="orig-key">官方页面摘录 · 报名期限</span>${deadlines.map(esc).join('<br>')}`:'',
    dates.length?`<span class="orig-key">官方页面摘录 · 考试日期</span>${dates.map(esc).join('<br>')}`:'',
    reqs.length?`<span class="orig-key">官方页面摘录 · 申请要求</span>${reqs.map(esc).join('<br>')}`:'',
    soft.length?`<span class="orig-key">官网页面其他信息</span>${soft.map(esc).join('<br>')}`:''
  ].filter(Boolean).join('<br><br>');
  return `<details class="cons-card${c.number>=300?' cons-card--academy':''}">
   <summary>
     <span class="cons-city">${esc(c.city)}</span>
     <span class="cons-school">${esc(c.school)}</span>
     <span class="cons-state ${stateClass(state)}">${esc(stateLabel(state))}</span>
     <span class="cons-line">${esc(consLine(c))}</span>
     <span class="cons-caret" aria-hidden="true">›</span>
   </summary>
   <div class="cons-body">
     ${zhBlocks?`<div class="cons-zh">${zhBlocks}</div>`:''}
     ${origBlocks?`<details class="cons-orig-wrap"><summary>查看官方原文与页面摘录</summary><div class="cons-orig">${origBlocks}${staleMark(said)}</div></details>`:''}
     <p class="cons-docs"><span class="docs-key">对应官方文件</span>
       ${locals.map((u,i)=>`<a class="doc-link doc-link--local" href="${esc(u)}" target="_blank" rel="noopener">站内文件 ${locals.length>1?i+1:''} ↓</a>`).join('')}
       ${docs.map(d=>`<a class="doc-link" href="${esc(d)}" target="_blank" rel="noopener">${esc(fileLabel(d))} ↗</a>`).join('')}
       <a class="doc-link" href="${esc(c.url)}" target="_blank" rel="noopener">院校官网 ↗</a>
     </p>
   </div>
 </details>`;
}
function filterInstitutionRecords(records,query,dateOnly){
  const q=normalizeSearch(query);
  return records.filter(c=>{
    const zh=c.zh||{};
    const searchable=[c.city,c.school,c.status,zh.state,...visibleCurrentLines(c.deadline_lines),...visibleCurrentLines(c.exam_dates),...visibleCurrentLines(c.requirements),...visibleCurrentLines(c.fallback_lines),...visibleCurrentLines(zh.d),...visibleCurrentLines(zh.x),...visibleCurrentLines(zh.r),...visibleCurrentLines(Array.isArray(zh.notes)?zh.notes:[zh.notes||''])].filter(Boolean).join(' ');
    if(q&&!normalizeSearch(searchable).includes(q))return false;
    if(dateOnly){
      const z=c.zh||{};
      const hasDate=Boolean(isoFromText((c.deadline_lines||[]).join(' '))||isoFromText((c.exam_dates||[]).join(' '))||zhIsoFromText((z.d||[]).join(' '))||zhIsoFromText((z.x||[]).join(' ')));
      if(!hasDate)return false;
    }
    return true;
  }).sort((a,b)=>{
    const oa=a.manual_status==='open'?1:0,ob=b.manual_status==='open'?1:0;
    if(ob!==oa)return ob-oa;
    const z=x=>isoFromText((x.deadline_lines||[]).join(' '))||zhIsoFromText(((x.zh||{}).d||[]).join(' '))||'9999';
    const da=z(a),db=z(b);
    if(da!==db)return da<db?-1:1;
    return String(a.city||'').localeCompare(String(b.city||''),'zh');
  });
}
function renderConservatori(){
  const wrap=$('#consGroups');
  if(!wrap)return;
  const schools=conservatoriData.filter(c=>(c.number||0)<300);
  const readable=schools.filter(c=>c.status==='ok');
  $('#conservatoriCount').textContent=`${readable.length}/${schools.length} 所院校页面可正常读取`;
  const filtered=filterInstitutionRecords(schools,consQuery,consDateOnly);
  const groups=filtered.length?[{title:'公立音乐学院',hint:'Conservatorio',items:filtered}]:[];
  wrap.innerHTML=groups.map(g=>`<section class="cons-group"><div class="cons-group-head"><h3>${g.title}</h3><span>${g.hint} · ${g.items.length} 所</span></div><div class="cons-list">${g.items.map(consCard).join('')}</div></section>`).join('');
  const emptyBox=$('#conservatoriEmpty');
  if(emptyBox)emptyBox.innerHTML=filtered.length?'':'<div class="empty">没有找到符合条件的公立音乐学院。请更换城市或调整筛选条件。</div>';
  renderTiles();
}
function renderAcademies(){
  const wrap=$('#academyGroups');
  if(!wrap)return;
  const programs=conservatoriData.filter(c=>['opera_academy','choral_school'].includes(c.institution_type));
  const filtered=filterInstitutionRecords(programs,academyQuery,academyDateOnly);
  const groups=[
    {title:'歌剧院 Accademia',hint:'Opera Academy',items:filtered.filter(c=>c.institution_type==='opera_academy')},
    {title:'剧院合唱学校',hint:'Choral School · 独立培养类别',items:filtered.filter(c=>c.institution_type==='choral_school')}
  ].filter(g=>g.items.length);
  wrap.innerHTML=groups.map(g=>`<section class="cons-group"><div class="cons-group-head"><h3>${g.title}</h3><span>${g.hint} · ${g.items.length} 个项目</span></div><div class="cons-list">${g.items.map(consCard).join('')}</div></section>`).join('');
  const total=programs.filter(c=>c.institution_type==='opera_academy').length;
  $('#academyCount').textContent=`${total} 个 Accademia · ${programs.filter(c=>c.institution_type==='choral_school').length} 个合唱学校`;
  const emptyBox=$('#academyEmpty');
  if(emptyBox)emptyBox.innerHTML=filtered.length?'':'<div class="empty">没有找到匹配的剧院学院或专业培养项目。</div>';
  renderTiles();
}

function renderTiles(){
  const callsCount=$('#opportunities')?$('#opportunities').querySelectorAll('.opportunity-card').length:0;
  const schools=conservatoriData.filter(c=>(c.number||0)<300);
  const readable=schools.filter(c=>c.status==='ok').length;
  const academyCount=conservatoriData.filter(c=>c.institution_type==='opera_academy').length;
  const set=(id,text)=>{const el=document.getElementById(id);if(el)el.textContent=text;};
  set('statCalls',callsCount?String(callsCount):'0');
  set('statSchools',schools.length?String(readable):'—');
  set('statAcademies',academyCount?String(academyCount):'—');
  set('statSongs',repertoireLoaded?String(repertoire.length):'—');
}

/* ---------- loading ---------- */
async function loadConservatori(){
  try{
    const [res,manual,zh,opportunityRes]=await Promise.all([
      fetch(new URL('data/conservatori.json',sourceRoot),{cache:'no-store'}),
      fetch(new URL('data/conservatori_manual.json',sourceRoot),{cache:'no-store'}).catch(()=>null),
      fetch(new URL('data/conservatori_zh.json',sourceRoot),{cache:'no-store'}).catch(()=>null),
      fetch(new URL('data/opportunities.json',sourceRoot),{cache:'no-store'}).catch(()=>null)
    ]);
    if(!res.ok)throw new Error(`HTTP ${res.status}`);
    const data=await res.json();
    conservatoriData=data.items||[];
    opportunities=[];
    if(opportunityRes&&opportunityRes.ok){
      const opportunityData=await opportunityRes.json();
      opportunities=opportunityData.items||[];
    }
    if(manual&&manual.ok){
      const m=await manual.json();
      manualNotes={};
      for(const entry of m.items||[])manualNotes[entry.number]=entry;
      for(const item of conservatoriData){
        const note=manualNotes[item.number];
        if(note&&note.zh)item.zh=Object.assign({},note.zh);
        if(note&&note.notes&&note.notes.length)item.zh=Object.assign({},item.zh||{},{notes:note.notes});
        if(note&&note.institution_type)item.institution_type=note.institution_type;
      }
    }
    if(zh&&zh.ok){
      const z=await zh.json();
      zhNotes=z.items||{};
      for(const item of conservatoriData){
        const note=zhNotes[String(item.number)];
        if(!note)continue;
        const merged=Object.assign({},item.zh||{});
        if(note.state)merged.state=note.state;
        if(note.d&&note.d.length)merged.d=note.d;
        if(note.x&&note.x.length)merged.x=note.x;
        if(note.r&&note.r.length)merged.r=note.r;
        item.zh=merged;
      }
    }
    const stamp=data.checked_at||(conservatoriData[0]||{}).checked_at;
    $('#updatedAt').textContent=stamp?`最近检查：${new Intl.DateTimeFormat('zh-CN',{timeZone:'Europe/Rome',month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'}).format(new Date(stamp))}`:'数据已载入';
  }catch(error){conservatoriData=[];opportunities=[];$('#updatedAt').textContent='暂时无法载入数据，请重新载入。';}
  renderConservatori();
  renderAcademies();
  renderCalls();
}

/* ---------- wiring ---------- */
function bindPanelLinks(){
  document.addEventListener('click',event=>{
    const opener=event.target.closest('[data-open]');
    if(opener&&!opener.classList.contains('lyrics-toggle')){
      const name=opener.dataset.open;
      if(document.getElementById(name)){event.preventDefault();openPanel(name);}
      return;
    }
    const back=event.target.closest('[data-back]');
    if(back){event.preventDefault();backToTiles();}
  });
}
bindPanelLinks();
$('#refreshButton').addEventListener('click',()=>{loadConservatori();loadRepertoire();});
const consInput=$('#consSearchInput');
if(consInput)consInput.addEventListener('input',event=>{consQuery=event.target.value;renderConservatori();});
const academyInput=$('#academySearchInput');
if(academyInput)academyInput.addEventListener('input',event=>{academyQuery=event.target.value;renderAcademies();});
const academyToggle=$('#academyDateOnly');
if(academyToggle)academyToggle.addEventListener('click',()=>{academyDateOnly=!academyDateOnly;academyToggle.setAttribute('aria-pressed',String(academyDateOnly));renderAcademies();});
const academyExpand=$('#academyExpandAll');
if(academyExpand)academyExpand.addEventListener('click',()=>{
  const on=academyExpand.getAttribute('aria-pressed')!=='true';
  academyExpand.setAttribute('aria-pressed',String(on));
  academyExpand.textContent=on?'收起全部项目':'展开全部项目';
  $('#academyGroups .cons-card').forEach(card=>{card.open=on;});
});
const consToggle=$('#consDateOnly');
if(consToggle)consToggle.addEventListener('click',()=>{consDateOnly=!consDateOnly;consToggle.setAttribute('aria-pressed',String(consDateOnly));renderConservatori();});
const expandAll=$('#consExpandAll');
if(expandAll)expandAll.addEventListener('click',()=>{
  const on=expandAll.getAttribute('aria-pressed')!=='true';
  expandAll.setAttribute('aria-pressed',String(on));
  expandAll.textContent=on?'收起全部院校':'展开全部院校';
  $$('.cons-card').forEach(card=>{card.open=on;});
});
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();installPrompt=event;$('#installButton').hidden=false;});
$('#installButton').addEventListener('click',async()=>{if(installPrompt){installPrompt.prompt();await installPrompt.userChoice;installPrompt=null;$('#installButton').hidden=true;}else{alert('请使用 Safari 打开本网站，点击“分享”，再选择“添加到主屏幕”。');}});
if(/iphone|ipad|ipod/i.test(navigator.userAgent)&&!window.navigator.standalone){$('#installButton').hidden=false;}
if('serviceWorker' in navigator && /^https?:$/.test(location.protocol))navigator.serviceWorker.register(new URL('service-worker.js',sourceRoot)).catch(()=>{});
$('#musicSearchForm').addEventListener('submit',event=>{event.preventDefault();renderMusicSearch($('#musicSearchInput').value);});
const musicVoiceFilter=$('#musicVoiceFilter');
if(musicVoiceFilter)musicVoiceFilter.addEventListener('change',()=>renderMusicSearch($('#musicSearchInput').value));
let musicSearchTimer=null;
$('#musicSearchInput').addEventListener('input',event=>{const value=event.target.value;clearTimeout(musicSearchTimer);musicSearchTimer=setTimeout(()=>renderMusicSearch(value),160);});
document.addEventListener('click',event=>{
  const suggest=event.target.closest('[data-suggest]');
  if(suggest){
    const value=suggest.dataset.suggest||'';
    $('#musicSearchInput').value=value;
    renderMusicSearch(value);
    const panel=document.getElementById('music-library');
    if(panel)panel.scrollIntoView({behavior:'smooth',block:'start'});
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
    toggle.textContent=open?'展开完整文本 ↓':'收起文本 ↑';
  }
});
$$('.search-chip').forEach(button=>button.addEventListener('click',()=>{const q=button.dataset.query;if(!q)return;$('#musicSearchInput').value=q;renderMusicSearch(q);}));
const sourcesLink=$('#sourcesLink');
if(sourcesLink)sourcesLink.addEventListener('click',event=>{const note=$('#sources-note');if(note){event.preventDefault();note.scrollIntoView({behavior:'smooth',block:'nearest'});}});
renderMusicSearch('');
renderTiles();
loadRepertoire();
loadConservatori();
