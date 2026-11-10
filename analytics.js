/* Privacy-conscious, optional Cloudflare Web Analytics loader. */
(() => {
  const config = window.OPERA_LIRICO_CONFIG || {};
  const token = typeof config.cloudflareWebAnalyticsToken === "string"
    ? config.cloudflareWebAnalyticsToken.trim()
    : "";
  if (!token || !/^[a-f0-9-]{16,}$/i.test(token)) return;
  if (document.querySelector('script[data-opera-lirico-analytics="cloudflare"]')) return;

  const script = document.createElement("script");
  script.defer = true;
  script.src = "https://static.cloudflareinsights.com/beacon.min.js";
  script.dataset.operaLiricoAnalytics = "cloudflare";
  script.dataset.cfBeacon = JSON.stringify({ token });
  document.head.appendChild(script);
})();
