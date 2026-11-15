/* Public site settings. Never put API keys or private credentials here. */
window.OPERA_LIRICO_CONFIG = Object.freeze({
  // Public Cloudflare Web Analytics site token.
  cloudflareWebAnalyticsToken: "42879f330b824eb4843baa5bd13ba002",
  newsletterUrl: "https://buttondown.com/wl19971007",
  archiveUrl: "https://buttondown.com/wl19971007/archive",
  // Public signup route on the operations Worker. No credentials are involved.
  subscribeEndpoint: "https://opera-lirico-ops.wl19971007.workers.dev/api/subscribe"
});
