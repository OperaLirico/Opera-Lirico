# Website analytics and newsletter setup

## Newsletter

The site links to the hosted Opera Lirico signup page:
https://buttondown.com/wl19971007

The signup is handled by Buttondown, not by a form hosted on this website. Subscribers can unsubscribe using the link included in Buttondown emails. Before promoting subscriptions, publish a privacy notice that identifies the data controller and contact address and explains Buttondown's role as a processor.

## Cloudflare Web Analytics

Analytics are deliberately disabled until the site owner configures a token.

1. Add the website to Cloudflare if it is not already there.
2. Open Web Analytics and add the exact public website hostname.
3. Copy the site's Web Analytics token (not an API token).
4. Edit `site-config.js` and set `cloudflareWebAnalyticsToken` to that value.
5. Leave it empty to disable analytics.

The loader only inserts Cloudflare's beacon script when a non-empty, valid-looking site token is configured. Do not put Cloudflare API tokens, account credentials, or other secrets in `site-config.js`; this file is public.

## Verification

- With an empty analytics token, no Cloudflare beacon request should be made.
- With a configured site token, inspect the browser Network panel for `beacon.min.js` and successful analytics collection.
- Test the Buttondown link in a private browser window and confirm the hosted signup page is reachable.
