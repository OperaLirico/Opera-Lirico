(() => {
  const section = document.querySelector('[data-moment="word-highlight"]');
  if (!section) return;
  const words = [...section.querySelectorAll('[data-word]')];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!words.length) return;
  document.documentElement.classList.add('taste-js');
  if (reduced) {
    words.forEach(word => word.classList.add('is-on'));
    return;
  }
  let queued = false;
  const update = () => {
    const rect = section.getBoundingClientRect();
    const start = window.innerHeight * 0.86;
    const end = window.innerHeight * 0.34;
    const progress = Math.max(0, Math.min(1, (start - rect.top) / (start - end + rect.height)));
    const active = Math.round(progress * words.length);
    words.forEach((word, index) => word.classList.toggle('is-on', index < active));
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
      words.forEach(word => word.classList.add('is-on'));
    }
  };
  const schedule = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; update(); });
  };
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  update();
})();