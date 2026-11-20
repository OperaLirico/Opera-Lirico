/* 首屏「最近截止」：直接读已渲染的开放项目面板，取最近三条，
   不重复请求数据，也不改 app.js 的取数与排序逻辑。 */
(function(){
  const host=document.getElementById('heroCalls');
  const box=document.getElementById('opportunities');
  const more=document.getElementById('heroCallsMore');
  if(!host||!box)return;
  let timer=0;

  function leftLabel(text){
    const m=String(text||'').match(/剩\s*\d+\s*(?:天|小时)|今天截止|明天截止/);
    return m?m[0].replace(/\s+/g,' '):'';
  }
  function dateLabel(text){
    const m=String(text||'').match(/报名截止[：:]\s*([^·]+)/);
    return m?m[1].trim():'';
  }
  function pick(card){
    const title=(card.querySelector('h3')||{}).textContent||'';
    const badge=(card.querySelector('.badge')||{}).textContent||'';
    const deadline=(card.querySelector('.deadline')||{}).textContent||'';
    const meta=[...card.querySelectorAll('.card-meta span')].map(s=>s.textContent.replace(/^\W+/,'').trim());
    const link=(card.querySelector('a.card-link')||{}).href||'#';
    return {title,badge,deadline,place:meta[0]||'',source:meta[1]||'',link};
  }
  function render(){
    const cards=[...box.querySelectorAll('.opportunity-card')];
    if(!cards.length){host.innerHTML='';return;}
    const top=cards.slice(0,3).map(pick);
    host.innerHTML=top.map(o=>{
      const left=leftLabel(o.deadline)||o.badge;
      const date=dateLabel(o.deadline);
      const where=[o.place,o.source].filter(Boolean).filter((v,i,a)=>a.indexOf(v)===i).join(' · ');
      return '<li class="hc-row"><a class="hc-link" href="'+o.link+'" target="_blank" rel="noopener">'+
        '<span class="hc-left">'+left+'</span>'+
        '<span class="hc-main"><strong>'+o.title+'</strong><small>'+where+'</small></span>'+
        '<span class="hc-date">'+(date?'截止 '+date:'')+'</span></a></li>';
    }).join('');
    if(more){
      more.hidden=false;
      more.textContent='看全部 '+cards.length+' 项 ↗';
    }
  }
  function schedule(){clearTimeout(timer);timer=setTimeout(render,80);}
  new MutationObserver(schedule).observe(box,{childList:true});
  schedule();
  document.addEventListener('operalab:refresh',schedule);
})();
