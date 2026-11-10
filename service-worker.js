const CACHE='vocal-italia-v17';
const SHELL=['./','./index.html','./styles.css','./app.js','./site-config.js','./analytics.js','./manifest.webmanifest','./icon.svg'];
self.addEventListener('install',event=>event.waitUntil(
  caches.open(CACHE).then(cache=>cache.addAll(SHELL)).then(()=>self.skipWaiting())
));
self.addEventListener('activate',event=>event.waitUntil(
  caches.keys()
    .then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key))))
    .then(()=>self.clients.claim())
));
// Same-origin assets change on every deploy, so the network is authoritative and the
// cache is only the offline fallback; a cached app.js must never mask a new release.
const freshFirst=(request,event)=>event.respondWith(
  fetch(request,{cache:'no-store'})
    .then(response=>{
      const copy=response.clone();
      caches.open(CACHE).then(cache=>cache.put(request,copy)).catch(()=>{});
      return response;
    })
    .catch(()=>caches.match(request))
);
self.addEventListener('fetch',event=>{
 const request=event.request;
 if(request.method!=='GET')return;
 const url=new URL(request.url);
 if(url.origin!==location.origin)return;
 const path=url.pathname;
 if(path.endsWith('/data/sources.json')||path.endsWith('/data/repertoire.json')||path.endsWith('/data/conservatori.json')||path.endsWith('/data/conservatori_extra.json')||path.endsWith('/data/conservatori_zh.json')||path.endsWith('/data/conservatori_manual.json')){
   freshFirst(request,event);
 }else if(request.mode==='navigate'||path.endsWith('/index.html')||/\.(?:css|js)$/.test(path)){
   freshFirst(request,event);
 }else{
   event.respondWith(caches.match(request).then(cached=>cached||fetch(request).then(response=>{
     const copy=response.clone();
     caches.open(CACHE).then(cache=>cache.put(request,copy)).catch(()=>{});
     return response;
   })));
 }
});
self.addEventListener('message',event=>{if(event.data==='skip-waiting')self.skipWaiting();});
