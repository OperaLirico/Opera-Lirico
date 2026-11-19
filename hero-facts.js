/* 首屏事实条：复用 #tiles 卡片区已经填好的统计，避免重复取数 */
(function () {
  var PAIRS = [
    ['statCalls', 'factCalls'],
    ['statSchools', 'factSchools'],
    ['statSongs', 'factSongs'],
    ['statMasterclasses', 'factMasterclasses']
  ];

  function sync() {
    var changed = false;
    for (var i = 0; i < PAIRS.length; i++) {
      var src = document.getElementById(PAIRS[i][0]);
      var dst = document.getElementById(PAIRS[i][1]);
      if (!src || !dst) continue;
      var v = (src.textContent || '').trim();
      if (!v || v === '—') continue;
      if (dst.textContent !== v) { dst.textContent = v; changed = true; }
    }
    return changed;
  }

  sync();

  var tiles = document.getElementById('tiles');
  if (tiles && typeof MutationObserver !== 'undefined') {
    new MutationObserver(sync).observe(tiles, { subtree: true, childList: true, characterData: true });
  }

  /* 数据较慢时的兼底轮询，最多约 10 秒 */
  var ticks = 0;
  var timer = setInterval(function () {
    if (sync() || ++ticks > 40) clearInterval(timer);
  }, 250);
})();
