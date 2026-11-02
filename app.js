const $ = (selector) => document.querySelector(selector);
const sourceRoot = new URL('.', location.href);
let sourceData = [];
let installPrompt = null;

const opportunities = [
  {title:'78° Concorso Internazionale AsLiCo per Giovani Cantanti Lirici 2027',category:'青年歌手选拔 · 歌剧角色招募',place:'科莫 · 多地预选',deadline:'2026-11-25T18:00:00+01:00',summary:'为 2027/28 OperaLombardia 歌剧季选拔演员，也设青年歌手组。招募角色包括《拉美莫尔的露琪亚》《伊多美纽》等；报名费 70 欧元。',url:'https://aslico.org/edizione-in-corso/',source:'AsLiCo'},
  {title:'Concorso Internazionale di Canto lirico Francesco Morlacchi 2026',category:'国际声乐比赛',place:'佩鲁贾',deadline:'2026-11-30T23:59:00+01:00',summary:'比赛将于 2026 年 12 月 14–15 日举行，面向 18 至 35 岁歌手。报名费 80 欧元，需提交曲目、简历、身份证明及演唱视频。',url:'https://www.concorsomorlacchi.it/',source:'Morlacchi 声乐比赛'}
];

const repertoire = [{"title":"Nessun dorma","aliases":["今夜无人入睡","今夜无人入眠","Turandot","图兰朵"],"composer":"Giacomo Puccini","work":"Turandot · 第三幕","voice":"男高音","kind":"咏叹调","text":"Nessun dorma! Nessun dorma!\nTu pure, o Principessa,\nnella tua fredda stanza,\nguardi le stelle che tremano\nd'amore e di speranza!\nMa il mio mistero è chiuso in me,\nil nome mio nessun saprà!\nNo, no! Sulla tua bocca lo dirò,\nquando la luce splenderà!\nEd il mio bacio scioglierà\nil silenzio che ti fa mia!\n(Il nome suo nessun saprà...)\nE noi dovrem, ahimè, morir, morir!\nDilegua, o notte!\nTramontate, stelle!\nTramontate, stelle!\nAll'alba vincerò!\nVincerò! Vincerò!","summary":"“无人入睡！公主也在寒夜里仰望星辰。等到黎明，我将赢得胜利。”","textSource":"https://imslp.org/wiki/Turandot_(Puccini,_Giacomo)","textSourceName":"IMSLP 作品页","scoreUrl":"https://imslp.org/wiki/Turandot_(Puccini,_Giacomo)"},{"title":"Voi che sapete","aliases":["你们可知道","费加罗的婚礼","Le nozze di Figaro","Cherubino"],"composer":"Wolfgang Amadeus Mozart","work":"Le nozze di Figaro · 第二幕","voice":"女中音 / 女低音","kind":"咏叹调","text":"Voi che sapete\nChe cosa è amor,\nDonne, vedete\nS’io l’ho nel cor.\nQuello ch’io provo\nVi ridirò;\nÈ per me nuovo,\nCapir nol so.\nSento un affetto\nPien di desir\nCh’ora è diletto,\nCh’ora è martir.\nGelo, e poi sento\nL’alma avvampar,\nE in un momento\nTorno a gelar.\nRicerco un bene\nFuori di me,\nNon so chi ’l tiene,\nNon so cos’è.\nSospiro e gemo\nSenza voler,\nPalpito e tremo\nSenza saper,\nNon trovo pace\nNotte né dì:\nMa pur mi piace\nLanguir così.\nVoi che sapete\nChe cosa è amor,\nDonne, vedete\nS’io l’ho nel cor.","summary":"“你们懂得什么是爱情，请告诉我心里是否有爱。它时而欢喜、时而煎熬，让我辗转难安。”","textSource":"https://it.wikisource.org/wiki/Le_nozze_di_Figaro/Atto_Secondo/Scena_terza","textSourceName":"Wikisource 原文","scoreUrl":"https://imslp.org/wiki/Le_nozze_di_Figaro,_K.492_(Mozart,_Wolfgang_Amadeus)"},{"title":"Libiamo ne’ lieti calici","aliases":["饮酒歌","祝酒歌","茶花女","La traviata","Brindisi"],"composer":"Giuseppe Verdi · 词：Francesco Maria Piave","work":"La traviata · 第一幕","voice":"女高音、男高音与合唱","kind":"咏叹调","text":"Alfredo\nLibiam ne’ lieti calici\nChe la bellezza infiora,\nE la fuggevol ora\nS’innebrii a voluttà.\nLibiam ne’ dolci fremiti\nChe suscita l’amore,\nPoichè quell’occhio al core\nOnnipotente va.\nTutti\nLibiamo; amor fra i calici\nPiù caldi baci avrà.\nVioletta\nTra voi, saprò dividere\nIl tempo mio giocondo;\nTutto è follia nel mondo\nCiò che non è piacer.\nGodiam, fugace e rapido\nÈ il gaudio dell’amore;\nÈ fior che nasce e muore,\nNè più si può goder.\nTutti\nGodiam... c’invita un fervido\nAccento lusinghier.\nGodiam... la tazza e il cantico\nLe notti abbella e il riso;\nIn questo paradiso\nNe scopra il nuovo dì.","summary":"宴会上举杯欢饮，维奥莱塔与阿尔弗雷多唱出关于青春、爱情与及时行乐的对答。","textSource":"https://it.wikisource.org/wiki/Pagina:La_traviata.djvu/7","textSourceName":"Wikisource 原文","scoreUrl":"https://imslp.org/wiki/La_traviata_(Verdi,_Giuseppe)"},{"title":"Casta Diva","aliases":["圣洁的女神","圣洁女神","诺尔玛","Norma"],"composer":"Vincenzo Bellini · 词：Felice Romani","work":"Norma · 第一幕","voice":"女高音","kind":"咏叹调","text":"Casta Diva, che inargenti\nQueste sacre antiche piante,\nA noi volgi il bel sembiante\nSenza nube e senza vel.\n\nTempra o Diva,\nTempra tu de’ cori ardenti,\nTempra ancor lo zelo audace,\nSpargi in terra quella pace\nChe regnar tu fai nel ciel.","summary":"诺尔玛向月之女神祈祷：请把宁静带到人间，平息众人炽烈的心。","textSource":"https://it.wikisource.org/wiki/Casta_Diva","textSourceName":"Wikisource 原文","scoreUrl":"https://imslp.org/wiki/Norma_(Bellini,_Vincenzo)"},{"title":"Ideale","aliases":["理想","Io ti seguii come iride di pace","托斯蒂"],"composer":"Francesco Paolo Tosti · 词：Carmelo Errico","work":"意大利艺术歌曲","voice":"男高音（常见）","kind":"艺术歌曲","text":"Io ti seguii come iride di pace\nLungo le vie del cielo:\nIo ti seguii come un’amica face\nDe la notte nel velo.\nE ti sentii ne la luce, ne l’aria,\nNel profumo dei fiori;\nE fu piena la stanza solitaria\nDi te, dei tuoi splendori.\n\nIn te rapito, al suon de la tua voce,\nLungamente sognai;\nE de la terra ogni affanno, ogni croce,\nIn quel giorno scordai.\nTorna, caro ideal, torna un istante\nA sorridermi ancora,\nE a me risplenderà, nel tuo sembiante,\nUna novella aurora.","summary":"歌者追忆心中的理想身影，盼望它再次归来，为自己带来新的黎明。","textSource":"https://www.lieder.net/lieder/get_text.html?RF=0&TextId=5465","textSourceName":"LiederNet 原文与出处","scoreUrl":"https://imslp.org/wiki/Ideale_(Tosti,_Francesco_Paolo)"},{"title":"Quanto t’amo","aliases":["我多么爱你","多么爱你","Matilde mia","Frontini"],"composer":"Francesco Paolo Frontini","work":"意大利艺术歌曲","voice":"男高音（常见）","kind":"艺术歌曲","text":"Quanto t’amo! quanto t’amo\nNon lo sai Matilde mia:\nLa tua voce udire io bramo,\nLa tua voce che m’india!\nLa tua voce che m’india!\nLa tua voce udire io bramo.\n\nO fanciulla, mio sospiro,\nVita mia, mio dolce bene,\nDeh! pietà di me deliro,\nDeh! pietà, deh! conforta le mie pene.\nMi rivolgi il tuo sorriso,\nIl tuo accento sospirato,\nVolerei nel paradiso\nPiù degli angeli beato.\nLa tua voce che m’india!\nLa tua voce udire io bramo.\nNon lo sai Matilde mia?\nQuanto t’amo! quanto t’amo!\nMatilde mia, quanto t’amo!","summary":"这首小夜曲以反复的告白表达思念：歌者渴望听见 Matilde 的声音，也盼她回应自己的爱意。","textSource":"https://it.wikisource.org/wiki/Quanto_t%27amo","textSourceName":"Wikisource 原文","scoreUrl":"https://imslp.org/wiki/Raccolta_per_canto_e_piano_1875-79_(Frontini,_Francesco_Paolo)"}];



function esc(text=''){return String(text).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));}
function renderMusicSearch(rawQuery){
 const target=$('#musicSearchResults');
 const query=rawQuery.trim();
 if(!query){
   target.innerHTML='<div class="music-empty">输入作品名即可查看歌词原文，再往下找乐谱。也可以点上面的热门曲目。</div>';
   return;
 }
 const terms=query.toLocaleLowerCase().split(/[\\/,，、;；|]+/).map(x=>x.trim()).filter(Boolean);
 const matches=repertoire.filter(item=>{
   const haystack=[item.title,...item.aliases,item.composer,item.work,item.kind].join(' ').toLocaleLowerCase();
   return terms.some(term=>haystack.includes(term));
 });
 if(!matches.length){
   const imslp='https://imslp.org/wiki/Special:Search?search='+encodeURIComponent(query);
   const textSearch='https://it.wikisource.org/wiki/Speciale:Ricerca?search='+encodeURIComponent(query);
   target.innerHTML=`<div class="music-empty"><strong>暂未收录这首作品的歌词。</strong><p>可以先去公开文本库或乐谱库搜索；新作品仍在整理中。</p><div class="music-actions"><a href="${esc(textSearch)}" target="_blank" rel="noopener">去 Wikisource 查文本 ↗</a><a href="${esc(imslp)}" target="_blank" rel="noopener">去 IMSLP 查乐谱 ↗</a></div></div>`;
   return;
 }
 target.innerHTML=matches.map(item=>`<article class="music-result">
   <div class="music-result-top"><span class="music-kind">${esc(item.kind)}</span><span class="music-voice">${esc(item.voice)}</span></div>
   <h3>${esc(item.title)}</h3>
   <p class="music-byline">${esc(item.composer)} · ${esc(item.work)}</p>
   <div class="music-text"><div class="music-text-label">歌词原文 · 意大利语</div><p class="lyrics">${esc(item.text).replace(/\n/g,'<br>')}</p></div>
   <p class="music-meaning"><strong>大意：</strong>${esc(item.summary)}</p>
   <div class="music-score"><div><span class="music-text-label">乐谱</span><p>在 IMSLP 查看可用版本、声部和下载选项。</p></div><a href="${esc(item.scoreUrl)}" target="_blank" rel="noopener">查看乐谱 ↗</a></div>
   <div class="music-source"><a href="${esc(item.textSource)}" target="_blank" rel="noopener">文本出处：${esc(item.textSourceName)} ↗</a></div>
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
loadData();
