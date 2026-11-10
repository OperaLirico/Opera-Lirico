# Per-source fetch strategy

## Current baseline

The production source registry currently contains 44 unique URLs in data/sources.json. The daily collector uses Scrapling for the fixed source list and the rotating legacy registry. data/source_fetch_policies.json records that as the current implementation, not as proof that Scrapling is optimal for every site.

Every source begins with strategy_status = baseline_only. No alternative is marked available until the exact official endpoint or feed is checked and tested.

## Assessment order

For each source, inspect in this order:

1. Official API or downloadable dataset.
2. RSS/Atom and sitemap.
3. Public JSON/XHR endpoint documented or visibly used by the official page.
4. Ordinary HTTP plus lxml/parsel for stable static HTML.
5. Existing Scrapling selector path for pages with changing markup.
6. Playwright only when required content is genuinely client-rendered and no permitted public endpoint exists.
7. curl_cffi only for a reproducible, permitted TLS/HTTP compatibility issue.

Do not introduce proxies, stealth, login sessions, CAPTCHA solving or access-control bypasses. A 403/429 or login wall is a monitoring blind spot, not an invitation to evade controls.

## Benchmark before switching

For a representative page snapshot, compare:
- field completeness: title, notice date, voice type, deadline, fee, age, eligibility, application link and PDF;
- extraction precision against first-party page evidence;
- runtime and request count;
- stability under small markup changes;
- dependency size and maintenance cost.

Keep the current method unless a repeatable test shows a clear improvement. Do not install all candidate libraries globally.

## Status

The policy registry is a coverage baseline only. P2 is not complete until each high-value source has an evidence-backed strategy assessment. Update the source policy entry with exact evidence URL, test date, chosen method and reason when that assessment is done.


## Redirect safety in the discovery pilot

The P2/P4 evaluation uses a same-host redirect handler. A cross-host redirect is not followed automatically: the destination host's robots.txt is checked first. If the destination robots policy is unavailable (except HTTP 404) or disallows the target path, the request stops and is recorded. A robots.txt file that itself redirects across hosts is treated as requiring manual review rather than followed blindly. This is conservative and may create a review item for legitimate CDN or canonical-host redirects; it must not be weakened by silently following redirects.
